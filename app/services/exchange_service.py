from app.models.inter_hospital_request import InterHospitalRequest
from app.models.inventory import Inventory


class ExchangeService:
    """
    High-level service that orchestrates inter-hospital blood exchange.
    All methods accept `db` as an explicit parameter to stay consistent
    with the rest of the codebase (no global import of db here).
    """

    # ── Dashboard stats ───────────────────────────────────────

    @staticmethod
    def get_exchange_stats(db, hospital_id):
        """
        Return a dict of counts for the admin dashboard widget.
        {
            "my_open":        int,   # broadcasts I raised that are still open/offered
            "my_accepted":    int,   # broadcasts I raised that got accepted
            "marketplace":    int,   # open broadcasts from OTHER hospitals
            "offers_placed":  int,   # offers I have placed on other hospitals' requests
        }
        """
        hid = str(hospital_id)
        pipeline_my = [
            {"$match": {"requester_hospital_id": hid}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        my_stats = {r["_id"]: r["count"]
                    for r in db.inter_hospital_requests.aggregate(pipeline_my)}

        marketplace_count = db.inter_hospital_requests.count_documents({
            "requester_hospital_id": {"$ne": hid},
            "status": {"$in": [InterHospitalRequest.OPEN,
                                InterHospitalRequest.OFFERED]},
        })

        # Count requests where this hospital has placed at least one offer
        offers_placed = db.inter_hospital_requests.count_documents({
            "requester_hospital_id": {"$ne": hid},
            "offers.supplier_hospital_id": hid,
        })

        my_open = (my_stats.get(InterHospitalRequest.OPEN, 0)
                   + my_stats.get(InterHospitalRequest.OFFERED, 0))

        return {
            "my_open":       my_open,
            "my_accepted":   my_stats.get(InterHospitalRequest.ACCEPTED, 0),
            "marketplace":   marketplace_count,
            "offers_placed": offers_placed,
        }

    # ── Listing helpers ───────────────────────────────────────

    @staticmethod
    def list_marketplace(db, hospital_id, page=1, per_page=10):
        """Open/offered requests from other hospitals for the marketplace view."""
        items, total = InterHospitalRequest.list_open_for_others(
            db, hospital_id, page=page, per_page=per_page
        )
        hid = str(hospital_id)
        for item in items:
            item["_id_str"] = str(item["_id"])
            # Has this admin's hospital already placed an offer?
            item["my_offer"] = next(
                (o for o in item.get("offers", [])
                 if o["supplier_hospital_id"] == hid),
                None,
            )
            item["offer_count"] = len(item.get("offers", []))
        return items, total

    @staticmethod
    def list_my_requests(db, hospital_id, page=1, per_page=10):
        """Requests broadcast by this hospital."""
        items, total = InterHospitalRequest.list_my_requests(
            db, hospital_id, page=page, per_page=per_page
        )
        for item in items:
            item["_id_str"] = str(item["_id"])
            item["offer_count"]   = len(item.get("offers", []))
            item["pending_offers"] = sum(
                1 for o in item.get("offers", [])
                if o["status"] == InterHospitalRequest.OFFER_PENDING
            )
        return items, total

    # ── Wraps model methods with inventory context ─────────────

    @staticmethod
    def complete_exchange(db, request_id, actor_id):
        """
        Fetch both inventories then delegate to the model.
        Returns (success: bool, message: str).
        """
        doc = InterHospitalRequest.get_by_id(db, request_id)
        if not doc:
            return False, "Request not found."

        # Find accepted offer to get supplier hospital
        accepted_offer = next(
            (o for o in doc.get("offers", [])
             if o["status"] == InterHospitalRequest.OFFER_ACCEPTED),
            None,
        )
        if not accepted_offer:
            return False, "No accepted offer found."

        supplier_id   = accepted_offer["supplier_hospital_id"]
        requester_id  = doc["requester_hospital_id"]

        supplier_inv  = Inventory.get_by_hospital(supplier_id, db)
        requester_inv = Inventory.get_by_hospital(requester_id, db)

        if not supplier_inv:
            return False, "Supplier hospital inventory not found."
        if not requester_inv:
            return False, "Requester hospital inventory not found."

        return InterHospitalRequest.complete_exchange(
            db, request_id, actor_id, supplier_inv, requester_inv
        )
