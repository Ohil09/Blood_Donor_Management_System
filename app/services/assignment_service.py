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
    @staticmethod
    def _unassigned_query():
        return {
            "role": "donor",
            "$or": [
                {"hospital_id": None},
                {"hospital_id": ""}
            ]
        }

    @staticmethod
    def get_unassigned_donors(db, skip=0, limit=None):
        """Get donors without hospital assignment (paged)."""
        query = AssignmentService._unassigned_query()
        cursor = db.users.find(query).sort("created_at", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    @staticmethod
    def count_unassigned_donors(db):
        """Count donors without hospital assignment."""
        query = AssignmentService._unassigned_query()
        return db.users.count_documents(query)
    
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
