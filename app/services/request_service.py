from app.services.inventory_service import InventoryService


class RequestService:
    """Service layer for blood request operations."""

    @staticmethod
    def get_matching_donors(blood_group, hospital_id, db):
        """Return eligible donors matching the given blood group (hospital-scoped first, then global)."""
        all_eligible_donors = InventoryService.search_donors_by_blood_group(
            blood_group, only_eligible=True, db=db
        )
        # Split into hospital-assigned and others
        assigned = [d for d in all_eligible_donors if d.get("hospital_id") == hospital_id]
        others = [d for d in all_eligible_donors if d.get("hospital_id") != hospital_id]

        # Enrich with eligibility metadata
        def enrich(donor):
            donor["_id_str"] = str(donor["_id"])
            donor["days_until_eligible"] = InventoryService.get_days_until_eligible(donor)
            donor["is_eligible"] = InventoryService.is_donor_eligible(donor)
            return donor

        return [enrich(d) for d in assigned], [enrich(d) for d in others]

    @staticmethod
    def get_request_stats(hospital_id, db):
        """Return counts of requests grouped by status for a hospital."""
        pipeline = [
            {"$match": {"hospital_id": hospital_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        results = list(db.blood_requests.aggregate(pipeline))
        stats = {r["_id"]: r["count"] for r in results}
        return stats
