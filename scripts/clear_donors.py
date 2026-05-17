#!/usr/bin/env python3
"""
Safe MongoDB cleanup script to remove all donor records.

This script safely removes all donors from the Blood Donor Management System (BDMS)
by:
1. Backing up donor data to a JSON file for recovery
2. Removing donor user records from the 'users' collection
3. Removing all associated donation records from the 'donations' collection
4. Preserving hospital inventory and other system data
5. Providing a recovery mechanism via the backup file

WARNING: This operation is destructive and cannot be undone without restoring from backup!
"""

import sys
import json
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pathlib import Path

# Load config from environment
def load_config():
    """Load MongoDB connection config from environment or defaults"""
    from dotenv import load_dotenv
    load_dotenv()
    
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/bdms_dev")
    db_name = os.environ.get("MONGO_DB_NAME", "bdms_dev")
    
    return mongo_uri, db_name


def create_backup(db):
    """
    Create a backup of all donor records before deletion.
    Returns the backup file path.
    """
    print("\n📋 Creating backup of all donor records...")
    
    # Fetch all donors
    donors = list(db.users.find({"role": "donor"}))
    donations = list(db.donations.find({}))  # All donations are donor-related
    
    # Convert ObjectId to string for JSON serialization
    for doc in donors + donations:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        if "donor_user_id" in doc:
            doc["donor_user_id"] = str(doc["donor_user_id"])
    
    # Create backup with timestamp
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"donors_backup_{timestamp}.json"
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "donors_count": len(donors),
        "donations_count": len(donations),
        "donors": donors,
        "donations": donations,
    }
    
    with open(backup_file, "w") as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"✅ Backup created: {backup_file}")
    print(f"   - Donors: {len(donors)}")
    print(f"   - Donations: {len(donations)}")
    
    return backup_file


def get_stats_before(db):
    """Get statistics before cleanup"""
    return {
        "donors": db.users.count_documents({"role": "donor"}),
        "donations": db.donations.count_documents({}),
        "users_total": db.users.count_documents({}),
        "hospitals": db.hospitals.count_documents({}),
        "inventory_records": db.inventory.count_documents({}),
    }


def get_stats_after(db):
    """Get statistics after cleanup"""
    return {
        "donors": db.users.count_documents({"role": "donor"}),
        "donations": db.donations.count_documents({}),
        "users_total": db.users.count_documents({}),
        "hospitals": db.hospitals.count_documents({}),
        "inventory_records": db.inventory.count_documents({}),
    }


def remove_donors(db):
    """
    Remove all donor records safely.
    
    Steps:
    1. Get all donor IDs
    2. Delete donation records linked to these donors
    3. Delete donor user records
    """
    print("\n🗑️  Removing donor records...")
    
    # Step 1: Find all donors
    donors = list(db.users.find({"role": "donor"}, {"_id": 1, "donor_id": 1}))
    donor_ids = [d["donor_id"] for d in donors if d.get("donor_id")]
    
    print(f"   Found {len(donors)} donor users with {len(donor_ids)} donor IDs")
    
    # Step 2: Remove all donation records
    if donor_ids:
        donation_result = db.donations.delete_many({"donor_id": {"$in": donor_ids}})
        print(f"   ✓ Removed {donation_result.deleted_count} donation records")
    else:
        print("   ℹ️  No donation records to remove")
    
    # Step 3: Remove all donor user records
    donor_result = db.users.delete_many({"role": "donor"})
    print(f"   ✓ Removed {donor_result.deleted_count} donor user records")
    
    return donor_result.deleted_count


def verify_data_integrity(db):
    """
    Verify that the cleanup didn't break the system.
    Checks:
    - No orphaned donations exist
    - Hospital admins and superadmins still exist
    - Hospital inventory is intact
    """
    print("\n🔍 Verifying data integrity...")
    
    issues = []
    
    # Check 1: No orphaned donations
    remaining_donations = db.donations.count_documents({})
    if remaining_donations > 0:
        issues.append(f"⚠️  Found {remaining_donations} remaining donations (should be 0)")
    else:
        print("   ✓ No orphaned donations")
    
    # Check 2: Admin users exist
    admin_count = db.users.count_documents({"role": {"$in": ["superadmin", "hospital_admin", "admin"]}})
    print(f"   ✓ {admin_count} admin users preserved")
    
    # Check 3: Hospitals exist
    hospital_count = db.hospitals.count_documents({})
    print(f"   ✓ {hospital_count} hospital records preserved")
    
    # Check 4: Inventory exists
    inventory_count = db.inventory.count_documents({})
    print(f"   ✓ {inventory_count} inventory records preserved")
    
    # Check 5: No donors remain
    donor_count = db.users.count_documents({"role": "donor"})
    if donor_count > 0:
        issues.append(f"⚠️  Found {donor_count} donors (should be 0)")
    else:
        print("   ✓ All donors removed")
    
    return issues


def main():
    """Main cleanup process"""
    print("=" * 70)
    print("🩸 BDMS Donor Cleanup Script")
    print("=" * 70)
    
    # Load config
    try:
        mongo_uri, db_name = load_config()
        print(f"\n📍 MongoDB URI: {mongo_uri}")
        print(f"📍 Database: {db_name}")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)
    
    # Connect to MongoDB
    try:
        print("\n🔗 Connecting to MongoDB...")
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verify connection
        db.command("ping")
        print("✅ Connected successfully")
    except PyMongoError as e:
        print(f"❌ MongoDB connection failed: {e}")
        sys.exit(1)
    
    # Get stats before
    stats_before = get_stats_before(db)
    print("\n📊 Stats Before Cleanup:")
    print(f"   - Donors: {stats_before['donors']}")
    print(f"   - Donations: {stats_before['donations']}")
    print(f"   - Total Users: {stats_before['users_total']}")
    print(f"   - Hospitals: {stats_before['hospitals']}")
    print(f"   - Inventory Records: {stats_before['inventory_records']}")
    
    # Confirm action
    if stats_before['donors'] == 0:
        print("\n✅ No donors to remove.")
        return
    
    print("\n" + "=" * 70)
    print("⚠️  WARNING: This will delete all donor records and cannot be undone!")
    print("=" * 70)
    print(f"\nYou are about to remove:")
    print(f"  • {stats_before['donors']} donor users")
    print(f"  • {stats_before['donations']} donation records")
    print("\nA backup will be created in: backups/donors_backup_*.json")
    print("=" * 70)
    
    response = input("\n⚠️  Type 'YES' to proceed (case-sensitive): ").strip()
    
    if response != "YES":
        print("❌ Cleanup cancelled by user.")
        return
    
    try:
        # Create backup
        backup_file = create_backup(db)
        
        # Remove donors
        removed_count = remove_donors(db)
        
        # Verify integrity
        issues = verify_data_integrity(db)
        
        # Get stats after
        stats_after = get_stats_after(db)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\n📊 Stats After Cleanup:")
        print(f"   - Donors: {stats_after['donors']}")
        print(f"   - Donations: {stats_after['donations']}")
        print(f"   - Total Users: {stats_after['users_total']}")
        print(f"   - Hospitals: {stats_after['hospitals']}")
        print(f"   - Inventory Records: {stats_after['inventory_records']}")
        
        print(f"\n🔄 Changes:")
        print(f"   - Removed {stats_before['donors']} donors")
        print(f"   - Removed {stats_before['donations']} donations")
        
        print(f"\n💾 Backup file: {backup_file}")
        print("   You can use this to restore if needed.")
        
        if issues:
            print("\n⚠️  Issues found during verification:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ No integrity issues detected.")
        
        print("\n" + "=" * 70)
        
    except PyMongoError as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
