# MongoDB Donor Cleanup Script - Safe Deletion Guide

## Overview

The `clear_donors.py` script safely removes all donor records from the Blood Donor Management System (BDMS) MongoDB database without breaking the application or losing critical data.

## What Gets Deleted

### ✅ What IS Removed
- **Donor Users** (`users` collection, `role: "donor"`)
  - User accounts for blood donors
  - Profile information (name, email, phone, blood group, etc.)
  - Donation history data (last_donation_date, next_eligible_date, donation_count)
  - Donor IDs (BDMS-XXXXXX format)

- **Donation Records** (`donations` collection)
  - All historical donation records linked to the removed donors
  - Donation dates, blood types, units, hospital assignments
  - Donation confirmations and notes

### ❌ What is NOT Affected
- ✅ Hospital data (`hospitals` collection)
- ✅ Hospital admin users (`users` with `role: "hospital_admin"`)
- ✅ System admins and superadmins
- ✅ Blood inventory data (`inventory` collection) - stays intact but may show inaccurate stock if donations are reused later
- ✅ Inter-hospital requests
- ✅ Other system configurations

## Safety Features

The script includes multiple safety mechanisms:

1. **Automatic Backup**
   - Creates a JSON backup file with timestamp: `backups/donors_backup_YYYYMMDD_HHMMSS.json`
   - Includes all donor and donation records for recovery
   - Backup is created BEFORE any deletion

2. **Explicit Confirmation**
   - Requires user to type "YES" (case-sensitive) to proceed
   - Shows statistics before deletion
   - Prevents accidental execution

3. **Data Integrity Verification**
   - Verifies no orphaned donations remain
   - Confirms all admin users are preserved
   - Checks hospital and inventory data integrity
   - Reports any issues found

4. **Non-Breaking Design**
   - Only deletes donor-specific records
   - Does not modify any application code
   - Does not affect authentication or authorization
   - Preserves database structure and indexes

## Prerequisites

```bash
# Install required Python package if not already installed
pip install pymongo python-dotenv
```

Ensure your environment is properly configured:
- MongoDB connection string in `.env` as `MONGO_URI`
- Database name in `.env` as `MONGO_DB_NAME` (defaults to `bdms_dev`)

## Usage

### Basic Usage

```bash
# From the project root directory
python scripts/clear_donors.py
```

### Step-by-Step Walkthrough

1. **Review Pre-Deletion Stats**
   - Script shows current donor and donation counts
   - Review the numbers carefully

2. **Read the Warning**
   - Script displays what will be deleted
   - Backup location is shown

3. **Confirm Action**
   - Type `YES` (uppercase, case-sensitive) to proceed
   - Type anything else to cancel

4. **Automatic Backup**
   - Backup is created to `backups/donors_backup_*.json`
   - File contains all deleted records

5. **Deletion Process**
   - Donors are removed from `users` collection
   - Donations are removed from `donations` collection
   - Database integrity is verified

6. **Review Results**
   - Script shows statistics after cleanup
   - Reports any integrity issues
   - Confirms backup location for recovery

## Recovery / Restore

If you need to restore the deleted data:

### Option 1: Using MongoDB Shell (Manual Restore)

```javascript
// Load the backup file
const backup = JSON.parse(fs.readFileSync('backups/donors_backup_YYYYMMDD_HHMMSS.json', 'utf8'));

// Convert string IDs back to ObjectId
backup.donors.forEach(d => d._id = ObjectId(d._id));
backup.donations.forEach(d => {
    d._id = ObjectId(d._id);
    d.donor_user_id = ObjectId(d.donor_user_id);
});

// Restore to database
db.users.insertMany(backup.donors);
db.donations.insertMany(backup.donations);
```

### Option 2: Create a Restore Script

You can create a Python restore script similar to the backup format:

```python
import json
from pymongo import MongoClient
from bson import ObjectId

# Load backup
with open('backups/donors_backup_YYYYMMDD_HHMMSS.json', 'r') as f:
    backup = json.load(f)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['bdms_dev']

# Convert string IDs back to ObjectId
for doc in backup['donors']:
    doc['_id'] = ObjectId(doc['_id'])

for doc in backup['donations']:
    doc['_id'] = ObjectId(doc['_id'])
    if 'donor_user_id' in doc and isinstance(doc['donor_user_id'], str):
        doc['donor_user_id'] = ObjectId(doc['donor_user_id'])

# Insert back
db.users.insert_many(backup['donors'])
db.donations.insert_many(backup['donations'])

print(f"✅ Restored {len(backup['donors'])} donors")
print(f"✅ Restored {len(backup['donations'])} donations")
```

## Common Use Cases

### Development/Testing
Use this script to clean up test donor data created during development:

```bash
# Create fresh test data
python scripts/create_superadmin.py
python scripts/create_hospital.py

# Create test donors via web interface or API

# Clean up when done
python scripts/clear_donors.py
```

### Database Reset
For full database reset scenarios (keeping hospital structure):

```bash
# Clear all donors
python scripts/clear_donors.py

# System is ready for fresh donor registrations
```

### Data Cleanup
Remove outdated or test donor records from production-like environments:

```bash
# Backup is automatically created
python scripts/clear_donors.py

# Original data is preserved in backup file
```

## Backup File Format

The backup file contains a JSON structure:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "donors_count": 150,
  "donations_count": 350,
  "donors": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "donor_id": "BDMS-ABC123",
      "full_name": "John Doe",
      "email": "john@example.com",
      "blood_group": "O+",
      "role": "donor",
      "is_active": true,
      ...
    },
    ...
  ],
  "donations": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "donor_id": "BDMS-ABC123",
      "donation_date": "2024-01-10T09:30:00.000000",
      "donation_type": "whole_blood",
      "blood_group": "O+",
      "units": 1,
      "hospital_id": "HOSP-XYZ",
      ...
    },
    ...
  ]
}
```

## Troubleshooting

### MongoDB Connection Error
```
Error: MongoDB connection failed
```

**Solution:**
- Verify MongoDB is running
- Check `MONGO_URI` in `.env` is correct
- Ensure network access to MongoDB server

### Permission Denied
```
Error during cleanup: not authorized on bdms_dev to execute command
```

**Solution:**
- MongoDB user needs `deleteDocument` privilege
- Verify credentials in `MONGO_URI`
- Check user has proper roles

### Backup Directory Error
```
Error: Backup directory not found
```

**Solution:**
- The script creates the `backups/` directory automatically
- If manual creation needed: `mkdir backups`

### No Donors Found
```
✅ No donors to remove.
```

**Solution:**
- This is normal if database is already clean
- Check if you're connected to the correct database

## Database Indexes

The script respects all existing MongoDB indexes:

- `db.users` indexes on `donor_id`, `email`, `role` are preserved
- `db.donations` indexes on `donor_id`, `hospital_id` are preserved
- Removing donors cascades correctly to donations due to referential cleanup

## Production Safety Checklist

Before running in production:

- [ ] Create a full database backup (not just donors)
- [ ] Test in staging/development environment first
- [ ] Notify stakeholders of the cleanup
- [ ] Verify backup file is created successfully
- [ ] Keep backup file in secure location
- [ ] Document the timestamp and reason for cleanup
- [ ] Run outside peak usage hours
- [ ] Monitor logs after cleanup

## Architecture Notes

### Collections Modified

1. **users** (`role: "donor"`)
   - Deletion method: `delete_many({"role": "donor"})`
   - Impact: Removes donor login accounts
   - Preserves: Hospital admins, superadmins, system admins

2. **donations**
   - Deletion method: `delete_many({"donor_id": {in: donor_ids}})`
   - Impact: Removes all donation history
   - No cascading: Direct deletion by donor ID

### Preserved Collections

- `hospitals` - Hospital records remain untouched
- `inventory` - Stock levels remain, but may not reflect historical accuracy
- `inter_hospital_requests` - Remain untouched
- Users with roles: `hospital_admin`, `superadmin`, `admin`

### Application Impact

- **Authentication**: Not affected, admin users still login normally
- **Routes**: All routes remain functional
- **Templates**: No template changes needed
- **Services**: Services handle missing donors gracefully

## Advanced: Custom Deletion Filters

If you want to delete only specific donors instead of all, you can modify the script:

```python
# Modify the remove_donors function:

# Example: Delete donors from specific city
donors = list(db.users.find({
    "role": "donor", 
    "city": "New York"  # Add filter here
}, {"_id": 1, "donor_id": 1}))

# Example: Delete donors inactive for 6 months
from datetime import datetime, timedelta, timezone
cutoff_date = datetime.now(timezone.utc) - timedelta(days=180)

donors = list(db.users.find({
    "role": "donor",
    "last_donation_date": {"$lt": cutoff_date}
}, {"_id": 1, "donor_id": 1}))
```

## Support and Questions

For issues or modifications:

1. Check the troubleshooting section above
2. Review MongoDB connection configuration
3. Verify backup file integrity
4. Check database permissions and roles

## License and Attribution

This script is part of the Blood Donor Management System (BDMS) and follows the same license as the main application.
