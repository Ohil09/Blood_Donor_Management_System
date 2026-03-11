import random
import string
from app import db

def generate_donor_id():
    """
    Generates a unique alphanumeric Donor ID in format: BDMS-XXXXXX
    Keeps retrying until a unique one is found.
    """
    while True:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        donor_id = f"BDMS-{suffix}"
        # Ensure uniqueness in DB
        existing = db.users.find_one({"donor_id": donor_id})
        if not existing:
            return donor_id