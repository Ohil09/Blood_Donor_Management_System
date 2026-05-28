import random
import string
from app import db


def generate_hospital_id(prefix="HOSP", length=4):
    """
    Generates a unique Hospital ID like HOSP-1234.
    Retries until unique in hospitals collection.
    """
    while True:
        suffix = "".join(random.choices(string.digits, k=length))
        hospital_id = f"{prefix}-{suffix}"
        if not db.hospitals.find_one({"hospital_id": hospital_id}):
            return hospital_id
