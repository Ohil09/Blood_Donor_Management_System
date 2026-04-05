# Single source of truth for blood group values used across models, forms, and services.
BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]

# WTForms-ready list of (value, label) tuples.
BLOOD_GROUP_CHOICES = [(bg, bg) for bg in BLOOD_GROUPS]
