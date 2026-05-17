from datetime import datetime


class InterHospitalRequest:
    STATUSES = {"pending", "approved", "rejected", "cancelled", "fulfilled"}

    def __init__(self, doc):
        self.id = str(doc.get("_id"))
        self.source_hospital_id = doc.get("source_hospital_id")
        self.source_hospital_name = doc.get("source_hospital_name")
        self.target_hospital_id = doc.get("target_hospital_id")
        self.target_hospital_name = doc.get("target_hospital_name")
        self.blood_group = doc.get("blood_group")
        self.units_required = int(doc.get("units_required", 0))
        self.urgency = doc.get("urgency")
        self.status = doc.get("status")
        self.preferred_fulfillment_date = doc.get("preferred_fulfillment_date")
        self.created_at = doc.get("created_at")
        self.updated_at = doc.get("updated_at")
        self.fulfilled_at = doc.get("fulfilled_at")
        self.audit = doc.get("audit", [])

    @staticmethod
    def format_dt(value):
        if not isinstance(value, datetime):
            return "-"
        return value.strftime("%d %b %Y, %I:%M %p")
