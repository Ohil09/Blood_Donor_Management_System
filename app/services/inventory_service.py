import re
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from flask import current_app
from app.models.inventory import Inventory
from app.constants import BLOOD_GROUPS

class InventoryService:
    """Service layer for inventory operations"""

    @staticmethod
    def get_or_create_inventory(hospital_id, hospital_name, db):
        """Get inventory or create if doesn't exist"""
        inventory = Inventory.get_by_hospital(hospital_id, db)
        if not inventory:
            inv_id = Inventory.init_for_hospital(hospital_id, hospital_name, db)
            doc = db.inventory.find_one({"_id": ObjectId(inv_id)})
            inventory = Inventory(doc)
        return inventory

    @staticmethod
    def search_donors_by_blood_group(blood_group, city=None, only_eligible=True, db=None):
        """Search donors matching blood group and filters.

        The city parameter is safely escaped before use in a MongoDB $regex
        query to prevent Regular Expression Denial of Service (ReDoS) attacks.
        """
        query = {"role": "donor", "blood_group": blood_group, "is_active": True}

        if city:
            query["city"] = {"$regex": re.escape(city), "$options": "i"}

        donors = list(db.users.find(query))

        if only_eligible:
            donors = [d for d in donors if InventoryService.is_donor_eligible(d)]

        return donors

    @staticmethod
    def is_donor_eligible(donor_doc):
        """Check if donor is eligible based on last donation date.

        Uses the WHOLE_BLOOD_INTERVAL from app config (default: 56 days).
        """
        last_donation = donor_doc.get("last_donation_date")

        if not last_donation:
            return True  # Never donated = eligible

        interval = current_app.config.get("WHOLE_BLOOD_INTERVAL", 56)
        next_eligible_date = last_donation + timedelta(days=interval)
        return datetime.now(timezone.utc) >= next_eligible_date

    @staticmethod
    def get_days_until_eligible(donor_doc):
        """Get days until donor is eligible again.

        Uses the WHOLE_BLOOD_INTERVAL from app config (default: 56 days).
        """
        last_donation = donor_doc.get("last_donation_date")

        if not last_donation:
            return 0

        interval = current_app.config.get("WHOLE_BLOOD_INTERVAL", 56)
        next_eligible_date = last_donation + timedelta(days=interval)
        days_left = (next_eligible_date - datetime.now(timezone.utc)).days
        return max(0, days_left)

    @staticmethod
    def get_low_stock_alert(inventory):
        """Generate low stock alert message"""
        low_groups = inventory.get_low_stock_groups()

        if not low_groups:
            return None

        return f"Low stock alert: {', '.join(low_groups)}"

    @staticmethod
    def get_inventory_stats(db):
        """Get system-wide inventory stats (for superadmin)"""
        all_inventory = list(db.inventory.find({}))

        total_units = 0
        blood_group_totals = {bg: 0 for bg in BLOOD_GROUPS}

        for inv_doc in all_inventory:
            inv = Inventory(inv_doc)
            total_units += inv.get_total_stock()
            for bg in BLOOD_GROUPS:
                blood_group_totals[bg] += inv.get_stock(bg)

        return {
            "total_units": total_units,
            "blood_group_totals": blood_group_totals,
            "hospitals_count": len(all_inventory),
        }