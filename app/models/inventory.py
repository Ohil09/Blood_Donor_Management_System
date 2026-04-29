from datetime import datetime, timezone
from bson import ObjectId

class Inventory:
    """Represents blood inventory for a hospital"""
    
    # Blood group constants
    BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    
    # Low stock threshold (units)
    LOW_STOCK_THRESHOLD = 10
    
    def __init__(self, inventory_doc):
        """Initialize from MongoDB document"""
        self.id = str(inventory_doc["_id"])
        self.hospital_id = inventory_doc.get("hospital_id")
        self.hospital_name = inventory_doc.get("hospital_name")
        self.stock = inventory_doc.get("stock", {})  # {"O+": 25, "A+": 15, ...}
        self.last_updated = inventory_doc.get("last_updated")
        self.created_at = inventory_doc.get("created_at")
    
    @staticmethod
    def init_for_hospital(hospital_id, hospital_name, db):
        """Create new inventory for a hospital"""
        inventory_doc = {
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "stock": {bg: 0 for bg in Inventory.BLOOD_GROUPS},
            "last_updated": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
        }
        result = db.inventory.insert_one(inventory_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_hospital(hospital_id, db):
        """Fetch inventory by hospital ID"""
        doc = db.inventory.find_one({"hospital_id": hospital_id})
        if not doc:
            return None
        return Inventory(doc)
    
    def get_stock(self, blood_group):
        """Get quantity for specific blood group"""
        return self.stock.get(blood_group, 0)
    
    def add_stock(self, blood_group, quantity, db):
        """Add units to stock"""
        if blood_group not in self.BLOOD_GROUPS:
            return False, "Invalid blood group"
        
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        new_quantity = self.get_stock(blood_group) + quantity
        
        db.inventory.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    f"stock.{blood_group}": new_quantity,
                    "last_updated": datetime.now(timezone.utc)
                }
            }
        )
        
        self.stock[blood_group] = new_quantity
        return True, f"Added {quantity} units of {blood_group}"
    
    def deplete_stock(self, blood_group, quantity, db):
        """Remove units from stock (donation fulfilled)"""
        if blood_group not in self.BLOOD_GROUPS:
            return False, "Invalid blood group"
        
        current = self.get_stock(blood_group)
        
        if quantity > current:
            return False, f"Insufficient stock. Available: {current} units"
        
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        new_quantity = current - quantity
        
        db.inventory.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    f"stock.{blood_group}": new_quantity,
                    "last_updated": datetime.now(timezone.utc)
                }
            }
        )
        
        self.stock[blood_group] = new_quantity
        return True, f"Depleted {quantity} units of {blood_group}"
    
    def is_low_stock(self, blood_group):
        """Check if blood group is below threshold"""
        return self.get_stock(blood_group) < self.LOW_STOCK_THRESHOLD
    
    def get_low_stock_groups(self):
        """Get list of blood groups below threshold"""
        return [bg for bg in self.BLOOD_GROUPS if self.is_low_stock(bg)]
    
    def get_total_stock(self):
        """Get total units across all blood groups"""
        return sum(self.stock.values())
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "id": self.id,
            "hospital_id": self.hospital_id,
            "hospital_name": self.hospital_name,
            "stock": self.stock,
            "total": self.get_total_stock(),
            "low_stock_groups": self.get_low_stock_groups(),
            "last_updated": self.last_updated.strftime("%d %b %Y, %I:%M %p") if self.last_updated else "N/A",
        }