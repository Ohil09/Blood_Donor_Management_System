from datetime import datetime, timezone, timedelta
from bson import ObjectId
from app.models.inventory import Inventory

class InventoryService:
    """Service layer for inventory operations"""
    
    @staticmethod
    def get_or_create_inventory(hospital_id, hospital_name, db):
        """Get inventory or create if doesn't exist"""
        inventory = Inventory.get_by_hospital(hospital_id, db)
        if not inventory:
            # Create new inventory
            inv_id = Inventory.init_for_hospital(hospital_id, hospital_name, db)
            doc = db.inventory.find_one({"_id": ObjectId(inv_id)})
            inventory = Inventory(doc)
        return inventory
    
    @staticmethod
    def search_donors_by_blood_group(blood_group, city=None, only_eligible=True, db=None):
        """Search donors matching blood group and filters"""
        query = {"role": "donor", "blood_group": blood_group, "is_active": True}
        
        if city:
            query["city"] = {"$regex": city, "$options": "i"}  # case-insensitive
        
        donors = list(db.users.find(query))
        
        # Filter by eligibility if requested
        if only_eligible:
            eligible_donors = []
            for donor in donors:
                if InventoryService.is_donor_eligible(donor):
                    eligible_donors.append(donor)
            donors = eligible_donors
        
        return donors
    
    @staticmethod
    def is_donor_eligible(donor_doc):
        """Check if donor is eligible based on last donation date"""
        last_donation = donor_doc.get("last_donation_date")
        
        if not last_donation:
            return True  # Never donated = eligible
        
        # 56 days for whole blood
        next_eligible_date = last_donation + timedelta(days=56)
        return datetime.now(timezone.utc) >= next_eligible_date
    
    @staticmethod
    def get_days_until_eligible(donor_doc):
        """Get days until donor is eligible again"""
        last_donation = donor_doc.get("last_donation_date")
        
        if not last_donation:
            return 0
        
        next_eligible_date = last_donation + timedelta(days=56)
        days_left = (next_eligible_date - datetime.now(timezone.utc)).days
        return max(0, days_left)
    
    @staticmethod
    def get_low_stock_alert(inventory):
        """Generate low stock alert message"""
        low_groups = inventory.get_low_stock_groups()
        
        if not low_groups:
            return None
        
        message = f"Low stock alert: {', '.join(low_groups)}"
        return message
    
    @staticmethod
    def get_inventory_stats(db):
        """Get system-wide inventory stats (for superadmin)"""
        all_inventory = list(db.inventory.find({}))
        
        total_units = 0
        blood_group_totals = {bg: 0 for bg in Inventory.BLOOD_GROUPS}
        
        for inv_doc in all_inventory:
            inv = Inventory(inv_doc)
            total_units += inv.get_total_stock()
            for bg in Inventory.BLOOD_GROUPS:
                blood_group_totals[bg] += inv.get_stock(bg)
        
        return {
            "total_units": total_units,
            "blood_group_totals": blood_group_totals,
            "hospitals_count": len(all_inventory),
        }