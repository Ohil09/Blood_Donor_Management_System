# BDMS Donor Cleanup Tool

Complete documentation and script for safely removing all blood donor records from MongoDB.

## 📚 Documentation Files

### 🟢 Start Here
- **[QUICK_START.md](QUICK_START.md)** - 30-second setup guide with example output

### 📖 Main Documentation
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Prerequisites and installation
- **[CLEAR_DONORS_GUIDE.md](CLEAR_DONORS_GUIDE.md)** - Complete user guide with troubleshooting
- **[DATABASE_IMPACT.md](DATABASE_IMPACT.md)** - Technical database analysis

### 🔧 The Script
- **[clear_donors.py](clear_donors.py)** - Main cleanup script

---

## ⚡ TL;DR - 3 Steps

```bash
# 1. Run the script
python scripts/clear_donors.py

# 2. Review the statistics shown
# 3. Type "YES" when prompted
# Done! Backup created to backups/donors_backup_*.json
```

---

## 🎯 What This Does

✅ **Removes**
- All donor user accounts
- All donation records

✅ **Preserves**
- Hospital data
- Hospital admin accounts
- Blood inventory
- System functionality

✅ **Guarantees**
- Automatic backup before deletion
- Data integrity verification
- Safe recovery options

---

## 📖 Which Document Should I Read?

| I want to... | Read this |
|-----------|-----------|
| Get started quickly (2 min) | [QUICK_START.md](QUICK_START.md) |
| Understand setup (5 min) | [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) |
| Learn everything (15 min) | [CLEAR_DONORS_GUIDE.md](CLEAR_DONORS_GUIDE.md) |
| Understand technical impact (15 min) | [DATABASE_IMPACT.md](DATABASE_IMPACT.md) |
| Just run it | `python clear_donors.py` |

---

## 🚀 Quick Run

```bash
cd D:\SBDMS
python scripts/clear_donors.py
```

Then:
1. **See** database statistics
2. **Read** the warning
3. **Type** `YES` (case-sensitive)
4. **Watch** backup creation
5. **Done** - backup saved to `backups/donors_backup_*.json`

---

## 📁 Files Generated

You'll see this after running:
```
backups/
└── donors_backup_YYYYMMDD_HHMMSS.json
```

This backup contains all deleted data for recovery if needed.

---

## ✅ Safety Features

| Feature | Benefit |
|---------|---------|
| Automatic Backup | Easy recovery |
| Explicit Confirmation | Prevents accidents |
| Pre/Post Statistics | See exactly what changed |
| Integrity Checks | Ensures database health |
| Reversible | Restore from backup anytime |

---

## 🔄 Recovery

If you need to restore:

1. **Find** the backup file in `backups/`
2. **Open** the JSON file (contains all deleted records)
3. **Follow** instructions in `CLEAR_DONORS_GUIDE.md` Section: "Recovery / Restore"
4. **Done** - donors restored

---

## ⚠️ Before You Run

- [ ] Have read [QUICK_START.md](QUICK_START.md)
- [ ] MongoDB is running
- [ ] `.env` file configured with MONGO_URI
- [ ] Understand you're deleting donor data (preserved in backup)
- [ ] Have ~10MB free space for backup

---

## 🐛 Troubleshooting

### Problem: MongoDB connection refused
**Solution:** 
- Check MongoDB is running
- Verify MONGO_URI in .env is correct
- See "Troubleshooting" in [CLEAR_DONORS_GUIDE.md](CLEAR_DONORS_GUIDE.md)

### Problem: "No module named pymongo"
**Solution:**
```bash
pip install pymongo[srv]
```

### Problem: "Permission denied"
**Solution:**
- Create backups directory: `mkdir backups`
- Check write permissions
- See full troubleshooting guide

---

## 📊 Example Output

```
🩸 BDMS Donor Cleanup Script

📊 Stats Before Cleanup:
   - Donors: 42
   - Donations: 156
   - Total Users: 47
   - Hospitals: 5

⚠️  Type 'YES' to proceed (case-sensitive): YES

✅ Backup created: backups/donors_backup_20240115_103045.json
   - Donors: 42
   - Donations: 156

✓ Removed 156 donation records
✓ Removed 42 donor user records

✅ CLEANUP COMPLETED SUCCESSFULLY

📊 Stats After Cleanup:
   - Donors: 0
   - Donations: 0
   - Total Users: 5
   - Hospitals: 5

💾 Backup file: backups/donors_backup_20240115_103045.json
```

---

## 🎓 Documentation Index

```
scripts/
├── README.md (you are here)
├── QUICK_START.md          ← START HERE
├── SETUP_INSTRUCTIONS.md   ← Installation & troubleshooting
├── CLEAR_DONORS_GUIDE.md   ← Complete guide & recovery
├── DATABASE_IMPACT.md      ← Technical analysis
└── clear_donors.py         ← The script

Root directory:
└── DONOR_CLEANUP_README.md ← Overview & links
```

---

## 🔗 Related Documents

From project root:
- **[DONOR_CLEANUP_README.md](../DONOR_CLEANUP_README.md)** - Overview (start if new to this tool)
- **[README.md](../README.md)** - Main project documentation

---

## 💬 Quick Questions

**Q: Will this break the application?**
A: No. Only donor data is deleted. Hospitals, admins, and inventory remain.

**Q: How do I restore if I change my mind?**
A: Use the backup file in `backups/`. See recovery guide in [CLEAR_DONORS_GUIDE.md](CLEAR_DONORS_GUIDE.md).

**Q: Can I delete only some donors?**
A: Current script deletes all. See "Advanced" section in [CLEAR_DONORS_GUIDE.md](CLEAR_DONORS_GUIDE.md) for custom filtering.

**Q: What if I type the wrong thing?**
A: The script cancels. Run it again and type `YES` correctly.

**Q: Where's my backup?**
A: `backups/donors_backup_YYYYMMDD_HHMMSS.json` - keep it safe!

---

## ✨ Next Steps

1. **New to this?** Read [QUICK_START.md](QUICK_START.md) (2 min)
2. **Ready to run?** Execute `python clear_donors.py`
3. **Need details?** See [CLEAR_DONORS_GUIDE.md](CLEAR_DONORS_GUIDE.md)
4. **Technical depth?** Study [DATABASE_IMPACT.md](DATABASE_IMPACT.md)

---

## 📝 Version Info

- **Version**: 1.0
- **Status**: Production Ready
- **Compatible With**: BDMS Application
- **MongoDB**: 4.0+
- **Python**: 3.7+

---

**Ready?** Run `python clear_donors.py` now!

For help: See the documentation files above.

