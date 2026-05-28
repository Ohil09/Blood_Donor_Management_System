from datetime import datetime, timedelta, timezone
from flask import current_app
from bson import ObjectId
from app.models.inventory import Inventory


class DonationService:
    DONATION_TYPE_TO_CONFIG = {
        "whole_blood": "WHOLE_BLOOD_INTERVAL",
        "platelets": "PLATELET_INTERVAL",
        "plasma": "PLASMA_INTERVAL",
    }

    @staticmethod
    def _interval_days(donation_type: str) -> int:
        key = DonationService.DONATION_TYPE_TO_CONFIG.get((donation_type or "").strip().lower(), "WHOLE_BLOOD_INTERVAL")
        return int(current_app.config.get(key, 56))

    @staticmethod
    def calculate_next_eligible_date(donation_date, donation_type: str):
        return donation_date + timedelta(days=DonationService._interval_days(donation_type))

    @staticmethod
    def ensure_indexes(db):
        db.donations.create_index([("donor_id", 1), ("donation_date", -1)])
        db.donations.create_index([("hospital_id", 1), ("donation_date", -1)])

    @staticmethod
    def record_donation(db, donor_doc, hospital_id, hospital_name, actor_id, donation_type="whole_blood", units=1, note=""):
        now = datetime.now(timezone.utc)
        next_eligible = DonationService.calculate_next_eligible_date(now, donation_type)
        donation_doc = {
            "donor_id": donor_doc["donor_id"],
            # "donor_user_id": str(donor_doc["_id"]),
            "donor_user_id": ObjectId(donor_doc["_id"]),
            "donor_name": donor_doc.get("full_name"),
            "blood_group": donor_doc.get("blood_group"),
            "donation_type": donation_type,
            "units": int(units),
            "donation_date": now,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "confirmed_by": str(actor_id),
            "note": note or "",
            "created_at": now,
        }
        db.donations.insert_one(donation_doc)

        prev_count = int(donor_doc.get("donation_count", 0))
        db.users.update_one(
            {"_id": donor_doc["_id"]},
            {"$set": {"last_donation_date": now, "next_eligible_date": next_eligible},
             "$inc": {"donation_count": 1}}
        )
        # Update inventory
        inventory = Inventory.get_by_hospital(hospital_id, db)
        if not inventory:
            Inventory.init_for_hospital(hospital_id, hospital_name, db)
            inventory = Inventory.get_by_hospital(hospital_id, db)

        inventory.add_stock(donor_doc.get("blood_group"), int(units), db)

        return {
            "donation_date": now,
            "next_eligible_date": next_eligible,
            "donation_count": prev_count + 1
        }
