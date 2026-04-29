import random
import string
from datetime import datetime, timezone
from bson import ObjectId


class BloodRequest:
    """Represents a blood donation request from a hospital."""

    BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    COMPONENT_TYPES = ["whole_blood", "plasma", "platelets"]
    URGENCY_LEVELS = ["low", "medium", "high", "emergency"]
    STATUSES = ["pending", "approved", "fulfilled", "rejected", "cancelled"]

    # Human-friendly labels
    COMPONENT_LABELS = {
        "whole_blood": "Whole Blood",
        "plasma": "Plasma",
        "platelets": "Platelets",
    }
    URGENCY_LABELS = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "emergency": "Emergency",
    }
    URGENCY_BADGE_CLASSES = {
        "low": "bg-secondary",
        "medium": "bg-info",
        "high": "bg-warning text-dark",
        "emergency": "bg-danger",
    }
    STATUS_BADGE_CLASSES = {
        "pending": "bg-warning text-dark",
        "approved": "bg-primary",
        "fulfilled": "bg-success",
        "rejected": "bg-danger",
        "cancelled": "bg-secondary",
    }

    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.request_id = doc.get("request_id", self.id)
        self.hospital_id = doc.get("hospital_id")
        self.hospital_name = doc.get("hospital_name")
        self.blood_group = doc.get("blood_group")
        self.component_type = doc.get("component_type", "whole_blood")
        self.units_required = doc.get("units_required", 1)
        self.urgency = doc.get("urgency", "medium")
        self.required_by_date = doc.get("required_by_date")
        self.patient_name = doc.get("patient_name")
        self.notes = doc.get("notes")
        self.status = doc.get("status", "pending")
        self.created_at = doc.get("created_at")
        self.updated_at = doc.get("updated_at")
        self.created_by = doc.get("created_by")
        self.fulfilled_units = doc.get("fulfilled_units", 0)
        self.fulfilled_at = doc.get("fulfilled_at")
        self.audit_trail = doc.get("audit_trail", [])

    # ── Class helpers ──────────────────────────────────────────────

    @property
    def component_label(self):
        return self.COMPONENT_LABELS.get(self.component_type, self.component_type)

    @property
    def urgency_label(self):
        return self.URGENCY_LABELS.get(self.urgency, self.urgency)

    @property
    def urgency_badge_class(self):
        return self.URGENCY_BADGE_CLASSES.get(self.urgency, "bg-secondary")

    @property
    def status_badge_class(self):
        return self.STATUS_BADGE_CLASSES.get(self.status, "bg-secondary")

    @property
    def required_by_date_display(self):
        if self.required_by_date:
            return self.required_by_date.strftime("%d %b %Y")
        return "N/A"

    @property
    def created_at_display(self):
        if self.created_at:
            return self.created_at.strftime("%d %b %Y, %I:%M %p")
        return "N/A"

    # ── Static / Class methods ─────────────────────────────────────

    @staticmethod
    def _generate_request_id():
        """Generate human-friendly request ID: REQ-YYYYMMDD-XXXX"""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"REQ-{date_str}-{suffix}"

    @staticmethod
    def create(data, db):
        """Insert a new blood request into the database."""
        now = datetime.now(timezone.utc)
        doc = {
            "request_id": BloodRequest._generate_request_id(),
            "hospital_id": data["hospital_id"],
            "hospital_name": data["hospital_name"],
            "blood_group": data["blood_group"],
            "component_type": data.get("component_type", "whole_blood"),
            "units_required": int(data["units_required"]),
            "urgency": data.get("urgency", "medium"),
            "required_by_date": data.get("required_by_date"),
            "patient_name": data.get("patient_name") or None,
            "notes": data.get("notes") or None,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "created_by": data["created_by"],
            "fulfilled_units": 0,
            "fulfilled_at": None,
            "audit_trail": [
                {
                    "status": "pending",
                    "timestamp": now,
                    "actor": data["created_by"],
                    "note": "Request created",
                }
            ],
        }
        result = db.blood_requests.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(request_id_str, db):
        """Fetch by MongoDB ObjectId string."""
        try:
            doc = db.blood_requests.find_one({"_id": ObjectId(request_id_str)})
        except Exception:
            doc = None
        return BloodRequest(doc) if doc else None

    @staticmethod
    def get_by_hospital(hospital_id, db, status=None, blood_group=None, page=1, per_page=10):
        """List requests for a hospital with optional filters + pagination."""
        query = {"hospital_id": hospital_id}
        if status:
            query["status"] = status
        if blood_group:
            query["blood_group"] = blood_group

        total = db.blood_requests.count_documents(query)
        docs = list(
            db.blood_requests.find(query)
            .sort("created_at", -1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        requests = [BloodRequest(d) for d in docs]
        total_pages = max(1, (total + per_page - 1) // per_page)
        return requests, total, total_pages

    def _update_status(self, new_status, actor_id, note, extra_set, db):
        """Internal: update status + audit trail."""
        now = datetime.now(timezone.utc)
        audit_entry = {
            "status": new_status,
            "timestamp": now,
            "actor": actor_id,
            "note": note,
        }
        set_fields = {"status": new_status, "updated_at": now, **extra_set}
        db.blood_requests.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": set_fields,
                "$push": {"audit_trail": audit_entry},
            },
        )
        self.status = new_status
        self.updated_at = now

    def approve(self, actor_id, db):
        if self.status != "pending":
            return False, "Only pending requests can be approved."
        self._update_status("approved", actor_id, "Request approved", {}, db)
        return True, "Request approved successfully."

    def reject(self, actor_id, reason, db):
        if self.status not in ("pending", "approved"):
            return False, "Request cannot be rejected in its current state."
        self._update_status("rejected", actor_id, reason or "Request rejected", {}, db)
        return True, "Request rejected."

    def cancel(self, actor_id, db):
        if self.status in ("fulfilled", "rejected", "cancelled"):
            return False, "Request is already in a terminal state."
        self._update_status("cancelled", actor_id, "Request cancelled", {}, db)
        return True, "Request cancelled."

    def fulfill(self, actor_id, units_provided, db):
        if self.status != "approved":
            return False, "Only approved requests can be fulfilled."
        if units_provided <= 0:
            return False, "Units provided must be positive."
        now = datetime.now(timezone.utc)
        self._update_status(
            "fulfilled",
            actor_id,
            f"Fulfilled with {units_provided} unit(s)",
            {"fulfilled_units": units_provided, "fulfilled_at": now},
            db,
        )
        return True, f"Request fulfilled with {units_provided} unit(s)."
