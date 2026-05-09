from datetime import datetime, timezone, date
from bson import ObjectId

class RequestService:
    VALID_STATUSES = {"pending", "awaiting_approval", "approved", "rejected", "cancelled", "fulfilled"}

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _add_audit(doc, action, actor_id, note=None):
        entry = {
            "at": RequestService._now(),
            "action": action,
            "actor_id": str(actor_id) if actor_id else None,
        }
        if note:
            entry["note"] = note
        doc.setdefault("audit", []).append(entry)

    @staticmethod
    def create_request(db, hospital_id, hospital_name, created_by,
                       blood_group, units_required, urgency,
                       preferred_fulfillment_date,
                       patient_name=None, notes=None,
                       available_units=0):
        """
        On submission: check inventory availability (pass available_units from route/service call).
        If enough stock: reserve units provisionally and set status awaiting_approval.
        Else: status pending and reserved_units=0.
        """
        sufficient = available_units >= units_required
        status = "awaiting_approval" if sufficient else "pending"
        reserved_units = units_required if sufficient else 0
        preferred_dt = preferred_fulfillment_date
        if isinstance(preferred_dt, date) and not isinstance(preferred_dt, datetime):
            preferred_dt = datetime(
                preferred_dt.year,
                preferred_dt.month,
                preferred_dt.day,
                tzinfo=timezone.utc
            )
        doc = {
            "hospital_id": str(hospital_id),
            "hospital_name": hospital_name,
            "blood_group": blood_group,
            "units_required": int(units_required),
            "reserved_units": int(reserved_units),
            "urgency": urgency,
            "preferred_fulfillment_date": preferred_dt,
            "patient_name": patient_name or "",
            "notes": notes or "",
            "status": status,
            "created_by": str(created_by),
            "created_at": RequestService._now(),
            "updated_at": RequestService._now(),
            "fulfilled_at": None,
        }

        RequestService._add_audit(
            doc,
            action="created",
            actor_id=created_by,
            note=f"available_units={available_units}, sufficient={sufficient}, reserved_units={reserved_units}"
        )

        result = db.requests.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def list_requests(db, hospital_id, status=None, blood_group=None, page=1, per_page=10):
        query = {"hospital_id": str(hospital_id)}
        if status:
            query["status"] = status
        if blood_group:
            query["blood_group"] = blood_group

        cursor = (db.requests.find(query)
                  .sort("created_at", -1)
                  .skip((page - 1) * per_page)
                  .limit(per_page))
        items = list(cursor)
        total = db.requests.count_documents(query)
        return items, total

    @staticmethod
    def get_request(db, request_id, hospital_id=None):
        try:
            oid = ObjectId(request_id)
        except Exception:
            return None
        q = {"_id": oid}
        if hospital_id:
            q["hospital_id"] = str(hospital_id)
        return db.requests.find_one(q)

    @staticmethod
    def approve_request(db, request_doc, actor_id):
        # Allowed: awaiting_approval -> approved
        if request_doc["status"] != "awaiting_approval":
            return False, "Only requests awaiting approval can be approved."

        update = {
            "$set": {"status": "approved", "updated_at": RequestService._now()},
            "$push": {"audit": {"at": RequestService._now(), "action": "approved", "actor_id": str(actor_id)}}
        }
        db.requests.update_one({"_id": request_doc["_id"]}, update)
        return True, "Request approved."

    @staticmethod
    def reject_request(db, request_doc, actor_id, reason=None):
        if request_doc["status"] in ("fulfilled", "cancelled", "rejected"):
            return False, "This request cannot be rejected now."

        # If it had reserved units, release them (by setting reserved_units=0)
        update = {
            "$set": {
                "status": "rejected",
                "reserved_units": 0,
                "updated_at": RequestService._now()
            },
            "$push": {"audit": {"at": RequestService._now(), "action": "rejected", "actor_id": str(actor_id), "note": reason or ""}}
        }
        db.requests.update_one({"_id": request_doc["_id"]}, update)
        return True, "Request rejected."

    @staticmethod
    def cancel_request(db, request_doc, actor_id):
        if request_doc["status"] in ("fulfilled", "cancelled"):
            return False, "This request cannot be cancelled."

        update = {
            "$set": {
                "status": "cancelled",
                "reserved_units": 0,
                "updated_at": RequestService._now()
            },
            "$push": {"audit": {"at": RequestService._now(), "action": "cancelled", "actor_id": str(actor_id)}}
        }
        db.requests.update_one({"_id": request_doc["_id"]}, update)
        return True, "Request cancelled."

    @staticmethod
    def fulfill_request(db, request_doc, actor_id, inventory_model):
        """
        Fulfilling will deplete inventory for the required blood group.
        Rules:
        - Only approved requests can be fulfilled.
        - Deplete exactly units_required.
        - Mark request fulfilled, reserved_units=0, fulfilled_at set.
        """
        if request_doc["status"] != "approved":
            return False, "Only approved requests can be fulfilled."

        blood_group = request_doc["blood_group"]
        units = int(request_doc["units_required"])

        success, msg = inventory_model.deplete_stock(blood_group, units, db)
        if not success:
            return False, f"Cannot fulfill: {msg}"

        update = {
            "$set": {
                "status": "fulfilled",
                "reserved_units": 0,
                "fulfilled_at": RequestService._now(),
                "updated_at": RequestService._now()
            },
            "$push": {"audit": {"at": RequestService._now(), "action": "fulfilled", "actor_id": str(actor_id), "note": f"depleted {units} of {blood_group}"}}
        }
        db.requests.update_one({"_id": request_doc["_id"]}, update)
        return True, "Request fulfilled and inventory depleted."