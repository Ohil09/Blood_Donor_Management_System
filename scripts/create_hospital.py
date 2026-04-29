import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from app import create_app

app = create_app()

with app.app_context():
    from app import db
    
    # Check if hospital exists
    existing = db.hospitals.find_one({"hospital_id": "hosp_001"})
    if existing:
        print("❌ Hospital already exists")
        sys.exit(1)
    
    # Create hospital
    result = db.hospitals.insert_one({
        "hospital_id": "hosp_001",
        "name": "City Hospital",
        "address": "123 Main Street, Mumbai",
        "city": "Mumbai",
        "phone": "9876543210",
        "email": "admin@cityhospital.com",
        "created_at": datetime.now(timezone.utc),
    })
    
    print("✅ Hospital created successfully!")
    print(f"🏥 Name: City Hospital")
    print(f"🏙️  City: Mumbai")
    print(f"📱 Phone: 9876543210")