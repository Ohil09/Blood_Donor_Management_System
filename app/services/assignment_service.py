from datetime import datetime, timezone
from bson import ObjectId

class AssignmentService:
    """Service for assigning donors to hospitals"""
    
    @staticmethod
    def assign_donor_to_hospital(donor_id, hospital_id, db):
        """Assign a donor to a hospital"""
        
        # Verify donor exists
        donor = db.users.find_one({"donor_id": donor_id})
        if not donor:
            return False, "Donor not found"
        
        # Verify hospital exists
        hospital = db.hospitals.find_one({"hospital_id": hospital_id})
        if not hospital:
            return False, "Hospital not found"
        
        # Update donor with hospital_id
        db.users.update_one(
            {"donor_id": donor_id},
            {
                "$set": {
                    "hospital_id": hospital_id,
                    "hospital_name": hospital.get("name"),
                }
            }
        )
        
        return True, f"Donor {donor_id} assigned to {hospital.get('name')}"
    
    @staticmethod
    def unassign_donor(donor_id, db):
        """Remove hospital assignment from donor"""
        
        db.users.update_one(
            {"donor_id": donor_id},
            {
                "$set": {
                    "hospital_id": None,
                    "hospital_name": None,
                }
            }
        )
        
        return True, "Donor unassigned from hospital"
    
    @staticmethod
    def get_unassigned_donors(db):
        """Get all donors without hospital assignment"""
        donors = list(
            db.users.find({
                "role": "donor",
                "$or": [
                    {"hospital_id": None},
                    {"hospital_id": ""}
                ]
            }).sort("created_at", -1)
        )
        return donors
    
    @staticmethod
    def get_assigned_donors(hospital_id, db):
        """Get all donors assigned to a hospital"""
        donors = list(
            db.users.find({
                "role": "donor",
                "hospital_id": hospital_id
            }).sort("created_at", -1)
        )
        return donors