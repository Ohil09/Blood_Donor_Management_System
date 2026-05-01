from datetime import datetime, timezone
from bson import ObjectId
import uuid


class InterHospitalRequest:
    """
    Represents a cross-hospital blood broadcast request.

    A hospital (requester) publishes an open broadcast when their inventory
    is insufficient.  Other hospitals (suppliers) can place supply offers.
    The requester picks one offer; completing the exchange updates both
    hospitals' inventories automatically.

    MongoDB collection: inter_hospital_requests

    Status machine:
        open  ──► offered  ──► accepted ──► completed
          └──────────────────────────────► cancelled
    Each individual offer also has its own status: pending | accepted | declined
    """

    BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    URGENCY_CHOICES = ["routine", "urgent", "critical"]
    COMPONENT_CHOICES = ["whole_blood", "plasma", "platelets"]

    OPEN      = "open"
    OFFERED   = "offered"
    ACCEPTED  = "accepted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    OFFER_PENDING  = "pending"
    OFFER_ACCEPTED = "accepted"
    OFFER_DECLINED = "declined"

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _audit_entry(action, actor_id, note=None):
        entry = {
            "at": InterHospitalRequest._now(),
            "action": action,
            "actor_id": str(actor_id) if actor_id else None,
        }
        if note:
            entry["note"] = note
        return entry

    # ── Create ────────────────────────────────────────────────

    @staticmethod
    def create(db, requester_hospital_id, requester_hospital_name,
               created_by, blood_group, component_type,
               units_needed, urgency, required_by_date, notes=None):
        """Insert a new open broadcast request and return the document."""
        doc = {
            "requester_hospital_id":   str(requester_hospital_id),
            "requester_hospital_name": requester_hospital_name,
            "blood_group":      blood_group,
            "component_type":   component_type,
            "units_needed":     int(units_needed),
            "urgency":          urgency,
            "required_by_date": required_by_date,
            "notes":            notes or "",
            "status":           InterHospitalRequest.OPEN,
            "created_by":       str(created_by),
            "created_at":       InterHospitalRequest._now(),
            "updated_at":       InterHospitalRequest._now(),
            "offers":           [],
            "audit": [
                InterHospitalRequest._audit_entry("created", created_by)
            ],
        }
        result = db.inter_hospital_requests.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    # ── Read ──────────────────────────────────────────────────

    @staticmethod
    def get_by_id(db, request_id):
        """Fetch one document by its string or ObjectId."""
        try:
            oid = ObjectId(request_id)
        except Exception:
            return None
        return db.inter_hospital_requests.find_one({"_id": oid})

    @staticmethod
    def list_open_for_others(db, hospital_id, page=1, per_page=10):
        """All open/offered broadcasts NOT created by hospital_id."""
        query = {
            "requester_hospital_id": {"$ne": str(hospital_id)},
            "status": {"$in": [InterHospitalRequest.OPEN, InterHospitalRequest.OFFERED]},
        }
        cursor = (
            db.inter_hospital_requests.find(query)
            .sort([("urgency_rank", -1), ("created_at", 1)])
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        items = list(cursor)
        total = db.inter_hospital_requests.count_documents(query)
        return items, total

    @staticmethod
    def list_my_requests(db, hospital_id, page=1, per_page=10):
        """All broadcasts created by this hospital."""
        query = {"requester_hospital_id": str(hospital_id)}
        cursor = (
            db.inter_hospital_requests.find(query)
            .sort("created_at", -1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        items = list(cursor)
        total = db.inter_hospital_requests.count_documents(query)
        return items, total

    # ── Offer ─────────────────────────────────────────────────

    @staticmethod
    def place_offer(db, request_id, supplier_hospital_id,
                    supplier_hospital_name, units_offered, offered_by, note=None):
        """
        Hospital B places a supply offer on an open/offered request.
        Returns (success: bool, message: str, offer_id: str | None).
        """
        doc = InterHospitalRequest.get_by_id(db, request_id)
        if not doc:
            return False, "Broadcast request not found.", None

        if doc["status"] not in (InterHospitalRequest.OPEN,
                                  InterHospitalRequest.OFFERED):
            return False, "This request is no longer open for offers.", None

        if doc["requester_hospital_id"] == str(supplier_hospital_id):
            return False, "You cannot offer blood to your own request.", None

        # Prevent duplicate offer from same hospital
        existing = [
            o for o in doc.get("offers", [])
            if o["supplier_hospital_id"] == str(supplier_hospital_id)
        ]
        if existing:
            return False, "Your hospital has already placed an offer on this request.", None

        offer_id = str(uuid.uuid4())
        offer = {
            "offer_id":              offer_id,
            "supplier_hospital_id":  str(supplier_hospital_id),
            "supplier_hospital_name": supplier_hospital_name,
            "units_offered":         int(units_offered),
            "offered_by":            str(offered_by),
            "offered_at":            InterHospitalRequest._now(),
            "status":                InterHospitalRequest.OFFER_PENDING,
            "response_note":         note or "",
        }

        # Push offer and audit entry together (MongoDB supports multiple fields under $push)
        audit_entry = InterHospitalRequest._audit_entry(
            "offer_placed", offered_by,
            note=f"supplier={supplier_hospital_name}, units={units_offered}"
        )
        db.inter_hospital_requests.update_one(
            {"_id": doc["_id"]},
            {
                "$push": {"offers": offer, "audit": audit_entry},
                "$set": {
                    "status":     InterHospitalRequest.OFFERED,
                    "updated_at": InterHospitalRequest._now(),
                },
            },
        )
        return True, "Offer submitted successfully.", offer_id

    # ── Accept an offer ───────────────────────────────────────

    @staticmethod
    def accept_offer(db, request_id, offer_id, actor_id):
        """
        Requester hospital accepts one offer.
        All other pending offers are declined automatically.
        Status becomes 'accepted'.
        """
        doc = InterHospitalRequest.get_by_id(db, request_id)
        if not doc:
            return False, "Request not found."

        if doc["status"] != InterHospitalRequest.OFFERED:
            return False, "No offers are available to accept."

        offer_found = False
        updated_offers = []
        for o in doc.get("offers", []):
            if o["offer_id"] == offer_id:
                offer_found = True
                o["status"] = InterHospitalRequest.OFFER_ACCEPTED
            elif o["status"] == InterHospitalRequest.OFFER_PENDING:
                o["status"] = InterHospitalRequest.OFFER_DECLINED
            updated_offers.append(o)

        if not offer_found:
            return False, "Offer not found."

        db.inter_hospital_requests.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "offers":     updated_offers,
                    "status":     InterHospitalRequest.ACCEPTED,
                    "updated_at": InterHospitalRequest._now(),
                },
                "$push": {
                    "audit": InterHospitalRequest._audit_entry(
                        "offer_accepted", actor_id, note=f"offer_id={offer_id}"
                    )
                },
            }
        )
        return True, "Offer accepted. Coordinate with the supplier hospital for the transfer."

    # ── Decline a specific offer ──────────────────────────────

    @staticmethod
    def decline_offer(db, request_id, offer_id, actor_id):
        """Requester declines a specific pending offer."""
        doc = InterHospitalRequest.get_by_id(db, request_id)
        if not doc:
            return False, "Request not found."

        if doc["status"] not in (InterHospitalRequest.OFFERED,
                                  InterHospitalRequest.OPEN):
            return False, "Cannot decline offers on this request."

        offer_found = False
        updated_offers = []
        for o in doc.get("offers", []):
            if o["offer_id"] == offer_id and o["status"] == InterHospitalRequest.OFFER_PENDING:
                offer_found = True
                o["status"] = InterHospitalRequest.OFFER_DECLINED
            updated_offers.append(o)

        if not offer_found:
            return False, "Offer not found or already resolved."

        # If no more pending offers, revert to 'open'
        remaining_pending = [o for o in updated_offers
                             if o["status"] == InterHospitalRequest.OFFER_PENDING]
        new_status = (InterHospitalRequest.OFFERED
                      if remaining_pending else InterHospitalRequest.OPEN)

        db.inter_hospital_requests.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "offers":     updated_offers,
                    "status":     new_status,
                    "updated_at": InterHospitalRequest._now(),
                },
                "$push": {
                    "audit": InterHospitalRequest._audit_entry(
                        "offer_declined", actor_id, note=f"offer_id={offer_id}"
                    )
                },
            }
        )
        return True, "Offer declined."

    # ── Complete ──────────────────────────────────────────────

    @staticmethod
    def complete_exchange(db, request_id, actor_id, supplier_inventory, requester_inventory):
        """
        Marks exchange as completed.
        - Depletes units_needed from supplier's inventory.
        - Adds units_needed to requester's inventory.
        - Status becomes 'completed'.
        """
        from app.models.inventory import Inventory

        doc = InterHospitalRequest.get_by_id(db, request_id)
        if not doc:
            return False, "Request not found."

        if doc["status"] != InterHospitalRequest.ACCEPTED:
            return False, "Only accepted exchanges can be completed."

        blood_group  = doc["blood_group"]
        units_needed = int(doc["units_needed"])

        # Deplete from supplier
        ok, msg = supplier_inventory.deplete_stock(blood_group, units_needed, db)
        if not ok:
            return False, f"Supplier inventory error: {msg}"

        # Credit requester
        requester_inventory.add_stock(blood_group, units_needed, db)

        db.inter_hospital_requests.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "status":       InterHospitalRequest.COMPLETED,
                    "completed_at": InterHospitalRequest._now(),
                    "updated_at":   InterHospitalRequest._now(),
                },
                "$push": {
                    "audit": InterHospitalRequest._audit_entry(
                        "completed", actor_id,
                        note=f"transferred {units_needed} units of {blood_group}"
                    )
                },
            }
        )
        return True, f"Exchange completed. {units_needed} units of {blood_group} transferred successfully."

    # ── Cancel ────────────────────────────────────────────────

    @staticmethod
    def cancel(db, request_id, actor_id):
        """Requester cancels an open/offered request."""
        doc = InterHospitalRequest.get_by_id(db, request_id)
        if not doc:
            return False, "Request not found."

        if doc["status"] in (InterHospitalRequest.COMPLETED,
                              InterHospitalRequest.CANCELLED):
            return False, "This request cannot be cancelled."

        if doc["status"] == InterHospitalRequest.ACCEPTED:
            return False, "An already-accepted exchange cannot be cancelled. Contact the supplier hospital directly."

        db.inter_hospital_requests.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "status":     InterHospitalRequest.CANCELLED,
                    "updated_at": InterHospitalRequest._now(),
                },
                "$push": {
                    "audit": InterHospitalRequest._audit_entry("cancelled", actor_id)
                },
            }
        )
        return True, "Broadcast request cancelled."
