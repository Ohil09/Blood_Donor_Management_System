import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from app import create_app

app = create_app()

# Import db AFTER app is created
from app import db

with app.app_context():
    # Create index
    db.donations.create_index([("donor_id", 1), ("donation_date", -1)])
    print("✅ Index created")

    # Get a real donor ID from your database
    donor = db.users.find_one({"role": "donor"})
    
    if not donor:
        print("❌ No donor found. Please register a donor first.")
        sys.exit(1)

    donor_id = donor["donor_id"]
    print(f"ℹ️  Using Donor ID: {donor_id}")

    # Insert sample donation
    db.donations.insert_one({
        "donor_id": donor_id,
        "blood_group": donor["blood_group"],
        "donation_type": "Whole Blood",
        "donation_date": datetime.now(timezone.utc),
        "hospital_name": "City Hospital"
    })
    print("✅ Sample donation inserted")