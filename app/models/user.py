from flask_login import UserMixin
from app import db

class User(UserMixin):
    """
    Wraps a MongoDB user document for Flask-Login.
    """
    def __init__(self, user_doc):
        self.id         = str(user_doc["_id"])
        self.donor_id   = user_doc.get("donor_id")
        self.full_name  = user_doc.get("full_name")
        self.email      = user_doc.get("email")
        self.phone      = user_doc.get("phone")
        self.role       = user_doc.get("role")
        self.blood_group= user_doc.get("blood_group")
        self.city       = user_doc.get("city")
        self.hospital_id= user_doc.get("hospital_id")
        self.is_active_account = user_doc.get("is_active", True)

    def get_id(self):
        return self.id

    @staticmethod
    def get_by_id(user_id):
        from bson import ObjectId
        doc = db.users.find_one({"_id": ObjectId(user_id)})
        return User(doc) if doc else None

    @staticmethod
    def get_by_donor_id(donor_id):
        doc = db.users.find_one({"donor_id": donor_id})
        return User(doc) if doc else None

    @staticmethod
    def get_by_email(email):
        doc = db.users.find_one({"email": email})
        return User(doc) if doc else None