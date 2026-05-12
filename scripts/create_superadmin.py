import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from app import create_app

app = create_app()

with app.app_context():
    from app import db

    existing = db.users.find_one({"email": "superadmin@bdms.com"})
    if existing:
        print("❌ Super Admin already exists")
        sys.exit(1)

    db.users.insert_one({
        "donor_id": None,
        "full_name": "Super Admin",
        "email": "superadmin@bdms.com",
        "phone": "9999999999",
        "role": "superadmin",
        "hospital_id": None,
        "hospital_name": None,
        "password_hash": generate_password_hash("superadmin123"),
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
        "city": "N/A",
    })

    print("✅ Super Admin created")
    print("Email: superadmin@bdms.com")
    print("Password: superadmin123")