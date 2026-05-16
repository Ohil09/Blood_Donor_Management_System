from datetime import datetime, timezone
from bson import ObjectId


class DonationRequest:
    """Represents a donor's willingness to donate blood at a specific hospital"""
    
    STATUSES = {"pending", "accepted", "rejected", "cancelled", "fulfilled"}
    BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    
    def __init__(self, doc):
        self.id = str(doc.get("_id"))
        self.donor_id = doc.get("donor_id")
        self.donor_user_id = doc.get("donor_user_id")
        self.donor_name = doc.get("donor_name")
        self.blood_group = doc.get("blood_group")
        self.hospital_id = doc.get("hospital_id")
        self.hospital_name = doc.get("hospital_name")
        self.units_offered = int(doc.get("units_offered", 1))
        self.urgency_level = doc.get("urgency_level", "normal")  # low, normal, high
        self.preferred_date = doc.get("preferred_date")
        self.additional_notes = doc.get("additional_notes", "")
        self.status = doc.get("status", "pending")
        self.created_at = doc.get("created_at")
        self.updated_at = doc.get("updated_at")
        self.accepted_at = doc.get("accepted_at")
        self.accepted_by = doc.get("accepted_by")  # Hospital admin user ID who accepted
        self.rejection_reason = doc.get("rejection_reason", "")
        self.audit = doc.get("audit", [])
    
    @staticmethod
    def format_dt(value):
        if not isinstance(value, datetime):
            return "-"
        return value.strftime("%d %b %Y, %I:%M %p")
    
    @staticmethod
    def format_date(value):
        if not isinstance(value, datetime):
            return "-"
        return value.strftime("%d %b %Y")
    
    def get_status_badge(self):
        """Return Bootstrap badge class for status"""
        badges = {
            "pending": "warning",
            "accepted": "success",
            "rejected": "danger",
            "cancelled": "secondary",
            "fulfilled": "info"
        }
        return badges.get(self.status, "secondary")
    
    def get_urgency_badge(self):
        """Return Bootstrap badge class for urgency"""
        badges = {
            "low": "info",
            "normal": "secondary",
            "high": "danger"
        }
        return badges.get(self.urgency_level, "secondary")
