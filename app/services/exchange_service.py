from datetime import datetime, timezone, date
from bson import ObjectId

from app.models.inventory import Inventory
class ExchangeService:
    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _as_utc_datetime(value):
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @staticmethod
    def _add_audit(doc, action, actor_id, note=None):
        event = {
            "at": ExchangeService._now(),
            "action": action,
            "actor_id": str(actor_id) if actor_id else None,
        }
        if note:
            event["note"] = note
        doc.setdefault("audit", []).append(event)

    @staticmethod
    def ensure_indexes(db):
        db.inter_hospital_requests.create_index([("source_hospital_id", 1), ("created_at", -1)])
        db.inter_hospital_requests.create_index([("target_hospital_id", 1), ("created_at", -1)])
        db.inter_hospital_requests.create_index([("status", 1), ("created_at", -1)])

    @staticmethod
    def create_exchange_request(
        db,
        source_hospital_id,
        source_hospital_name,
        target_hospital_id,
        created_by,
        blood_group,
        units_required,
        urgency,
        preferred_fulfillment_date,
        patient_name=None,
        notes=None,
    ):
        source_hospital_id = str(source_hospital_id)
        target_hospital_id = str(target_hospital_id)

        if source_hospital_id == target_hospital_id:
            return False, "Source and target hospital cannot be the same.", None

        target_hospital = db.hospitals.find_one({"hospital_id": target_hospital_id})
        if not target_hospital:
            return False, "Target hospital was not found.", None

        doc = {
            "source_hospital_id": source_hospital_id,
            "source_hospital_name": source_hospital_name,
            "target_hospital_id": target_hospital_id,
            "target_hospital_name": target_hospital.get("name") or "Unknown Hospital",
            "blood_group": blood_group,
            "units_required": int(units_required),
            "urgency": urgency,
            "preferred_fulfillment_date": ExchangeService._as_utc_datetime(preferred_fulfillment_date),
            "patient_name": patient_name or "",
            "notes": notes or "",
            "status": "pending",
            "created_by": str(created_by),
            "approved_by": None,
            "fulfilled_by": None,
            "created_at": ExchangeService._now(),
            "updated_at": ExchangeService._now(),
            "fulfilled_at": None,
            "audit": [],
        }
        ExchangeService._add_audit(doc, "created", created_by, note=f"to={target_hospital_id}")
        result = db.inter_hospital_requests.insert_one(doc)
        doc["_id"] = result.inserted_id
        return True, "Exchange request sent successfully.", doc

    @staticmethod
    def list_requests(db, hospital_id, scope="all", status=None, blood_group=None, page=1, per_page=10):
        hospital_id = str(hospital_id)
        if scope == "inbound":
            query = {"target_hospital_id": hospital_id}
        elif scope == "outbound":
            query = {"source_hospital_id": hospital_id}
        else:
            query = {"$or": [{"source_hospital_id": hospital_id}, {"target_hospital_id": hospital_id}]}

        if status:
            query["status"] = status
        if blood_group:
            query["blood_group"] = blood_group

        cursor = (
            db.inter_hospital_requests.find(query)
            .sort("created_at", -1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        items = list(cursor)
        total = db.inter_hospital_requests.count_documents(query)
        return items, total

    @staticmethod
    def get_request(db, exchange_request_id, hospital_id=None):
        try:
            oid = ObjectId(exchange_request_id)
        except Exception:
            return None
        query = {"_id": oid}
        if hospital_id:
            query["$or"] = [
                {"source_hospital_id": str(hospital_id)},
                {"target_hospital_id": str(hospital_id)},
            ]
        return db.inter_hospital_requests.find_one(query)

    @staticmethod
    def get_actor_role(request_doc, hospital_id):
        hospital_id = str(hospital_id)
        if request_doc.get("source_hospital_id") == hospital_id:
            return "source"
        if request_doc.get("target_hospital_id") == hospital_id:
            return "target"
        return None

    @staticmethod
    def approve_request(db, request_doc, actor_id, actor_hospital_id, target_inventory):
        if request_doc.get("status") != "pending":
            return False, "Only pending requests can be approved."
        if ExchangeService.get_actor_role(request_doc, actor_hospital_id) != "target":
            return False, "Only target hospital can approve this request."

        blood_group = request_doc.get("blood_group")
        units_required = int(request_doc.get("units_required", 0))
        available = target_inventory.get_stock(blood_group)
        if available < units_required:
            return False, f"Insufficient stock for approval. Available: {available} units."

        db.inter_hospital_requests.update_one(
            {"_id": request_doc["_id"]},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": str(actor_id),
                    "updated_at": ExchangeService._now(),
                },
                "$push": {
                    "audit": {
                        "at": ExchangeService._now(),
                        "action": "approved",
                        "actor_id": str(actor_id),
                        "note": f"available={available}",
                    }
                },
            },
        )
        return True, "Exchange request approved."

    @staticmethod
    def reject_request(db, request_doc, actor_id, actor_hospital_id):
        if request_doc.get("status") in {"fulfilled", "cancelled", "rejected"}:
            return False, "This request cannot be rejected now."
        if ExchangeService.get_actor_role(request_doc, actor_hospital_id) != "target":
            return False, "Only target hospital can reject this request."

        db.inter_hospital_requests.update_one(
            {"_id": request_doc["_id"]},
            {
                "$set": {"status": "rejected", "updated_at": ExchangeService._now()},
                "$push": {
                    "audit": {
                        "at": ExchangeService._now(),
                        "action": "rejected",
                        "actor_id": str(actor_id),
                    }
                },
            },
        )
        return True, "Exchange request rejected."

    @staticmethod
    def cancel_request(db, request_doc, actor_id, actor_hospital_id):
        if request_doc.get("status") in {"fulfilled", "cancelled", "rejected"}:
            return False, "This request cannot be cancelled."
        if ExchangeService.get_actor_role(request_doc, actor_hospital_id) != "source":
            return False, "Only source hospital can cancel this request."

        db.inter_hospital_requests.update_one(
            {"_id": request_doc["_id"]},
            {
                "$set": {"status": "cancelled", "updated_at": ExchangeService._now()},
                "$push": {
                    "audit": {
                        "at": ExchangeService._now(),
                        "action": "cancelled",
                        "actor_id": str(actor_id),
                    }
                },
            },
        )
        return True, "Exchange request cancelled."

    @staticmethod
    def fulfill_request(db, request_doc, actor_id, actor_hospital_id, target_inventory):
        if request_doc.get("status") != "approved":
            return False, "Only approved requests can be fulfilled."
        if ExchangeService.get_actor_role(request_doc, actor_hospital_id) != "target":
            return False, "Only target hospital can fulfill this request."

        blood_group = request_doc.get("blood_group")
        units_required = int(request_doc.get("units_required", 0))

        ok, msg = target_inventory.deplete_stock(blood_group, units_required, db)
        if not ok:
            return False, f"Could not fulfill: {msg}"

        source_hospital_id = request_doc.get("source_hospital_id")
        source_hospital_name = request_doc.get("source_hospital_name") or "Unknown Hospital"
        source_inventory = Inventory.get_by_hospital(source_hospital_id, db)
        if not source_inventory:
            Inventory.init_for_hospital(source_hospital_id, source_hospital_name, db)
            source_inventory = Inventory.get_by_hospital(source_hospital_id, db)

        ok_add, msg_add = source_inventory.add_stock(blood_group, units_required, db)
        if not ok_add:
            return False, f"Transfer failed after deplete: {msg_add}"

        db.inter_hospital_requests.update_one(
            {"_id": request_doc["_id"]},
            {
                "$set": {
                    "status": "fulfilled",
                    "fulfilled_by": str(actor_id),
                    "fulfilled_at": ExchangeService._now(),
                    "updated_at": ExchangeService._now(),
                },
                "$push": {
                    "audit": {
                        "at": ExchangeService._now(),
                        "action": "fulfilled",
                        "actor_id": str(actor_id),
                        "note": f"transferred {units_required} units of {blood_group}",
                    }
                },
            },
        )
        return True, "Exchange request fulfilled. Units transferred successfully."
