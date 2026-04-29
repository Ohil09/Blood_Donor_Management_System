import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from app import create_app

app = create_app()

with app.app_context():
    from app import db
    
    # Check if admin already exists
    existing = db.users.find_one({"email": "admin@hospital.com"})
    if existing:
        print("❌ Admin already exists with this email")
        sys.exit(1)
    
    # Create admin user
    result = db.users.insert_one({
        "donor_id": None,
        "full_name": "Hospital Admin",
        "email": "admin@hospital.com",
        "phone": "9876543210",
        "role": "admin",
        "hospital_id": "hosp_001",
        "hospital_name": "City Hospital",
        "password_hash": generate_password_hash("admin123"),
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
        "age": 30,
        "gender": "Male",
        "blood_group": "O+",
        "city": "Mumbai"
    })
    
    print("✅ Admin created successfully!")
    print(f"📧 Email: admin@hospital.com")
    print(f"🔑 Password: admin123")
    print(f"🏥 Hospital ID: hosp_001")