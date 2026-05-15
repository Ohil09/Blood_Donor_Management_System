# 📧 Email Configuration Setup Guide

## Overview
The Blood Donor Management System (BDMS) uses email notifications to:
- **Donors**: Send welcome messages with unique Donor ID
- **Hospitals**: Send admin credentials after registration by superadmin

## Prerequisites
- Python 3.8+
- Flask-Mail installed (`pip install flask-mail`)
- Email account with SMTP access

## Email Providers Setup

### 🔵 Gmail (Recommended for Development)

#### Step 1: Enable 2-Step Verification
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)

#### Step 2: Generate App Password
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Windows Computer** (or your OS)
3. Google will generate a **16-character app password**
4. Copy this password (it won't be shown again)

#### Step 3: Update .env File
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

⚠️ **Important**: 
- Use your actual Gmail address, not a placeholder
- The app password is the 16-character code Google generated
- Include spaces exactly as shown by Google
- Do NOT use your Gmail password directly

---

### 🟠 Outlook / Hotmail

```
MAIL_SERVER=smtp.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=your_email@outlook.com
```

---

### 🟢 SendGrid (Production Recommended)

#### Step 1: Create SendGrid Account
1. Sign up at [SendGrid](https://sendgrid.com)
2. Create API Key from Settings → API Keys

#### Step 2: Update .env File
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your_api_key_here
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

---

### 🟡 AWS SES (Amazon)

```
MAIL_SERVER=email-smtp.region.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_smtp_username
MAIL_PASSWORD=your_smtp_password
MAIL_DEFAULT_SENDER=verified_sender@yourdomain.com
```

---

## Features

### 1️⃣ Donor Registration Email
**Trigger**: When a donor registers

**What's included**:
- Beautiful welcome message
- Unique Donor ID (e.g., BDMS-AB1234)
- Next steps to get started
- Impact message about blood donation

**Template**: [Beautiful HTML template with gradient design]

---

### 2️⃣ Hospital Admin Credentials Email
**Trigger**: When superadmin creates a new hospital

**What's included**:
- Hospital ID
- Admin login credentials (username/email)
- Temporary password
- Security warnings
- Quick start guide

**Template**: [Professional HTML template with blue gradient]

---

## Testing Email Configuration

### Method 1: Using Python REPL
```python
from app import create_app, mail
from flask_mail import Message

app = create_app()

with app.app_context():
    msg = Message(
        subject="Test Email from BDMS",
        recipients=["your_test_email@gmail.com"],
        body="This is a test email from BDMS!"
    )
    mail.send(msg)
    print("✅ Email sent successfully!")
```

### Method 2: Run Registration
1. Go to registration page
2. Register a new donor account
3. Check email inbox for welcome message

---

## Troubleshooting

### ❌ "SMTPAuthenticationError"
**Problem**: Username/password incorrect

**Solution**:
- Verify MAIL_USERNAME is correct email address
- For Gmail: Use app password (16 chars), not Gmail password
- For Outlook: Use your actual password
- Check for trailing/leading spaces

---

### ❌ "SMTPNotSupportedError"
**Problem**: TLS not supported

**Solution**:
```
MAIL_USE_TLS=True    # Try this first
# OR if that fails:
MAIL_USE_TLS=False
MAIL_PORT=465        # Use SSL instead
```

---

### ❌ "Connection refused / Timeout"
**Problem**: Can't connect to SMTP server

**Solution**:
- Verify MAIL_SERVER spelling
- Check MAIL_PORT (usually 587 for TLS, 465 for SSL)
- Check internet connection
- Try a different email provider

---

### ❌ "Email not received"
**Problem**: Email sent but not in inbox

**Solution**:
- Check spam/junk folder
- Verify MAIL_DEFAULT_SENDER matches sender email
- Check email provider logs
- Try sending to a different email address

---

## Environment Variable Reference

```bash
# Email Server (required)
MAIL_SERVER=smtp.gmail.com              # SMTP server address
MAIL_PORT=587                           # Usually 587 (TLS) or 465 (SSL)
MAIL_USE_TLS=True                       # Use TLS encryption

# Authentication (required)
MAIL_USERNAME=your_email@gmail.com      # Your email address
MAIL_PASSWORD=app_password              # App-specific password
MAIL_DEFAULT_SENDER=your_email@gmail.com # Reply-from address

# Donor Registration Email
# Automatic: Sends when form.validate_on_submit() succeeds

# Hospital Creation Email
# Automatic: Sends when superadmin creates hospital via form
```

---

## Implementation Details

### Email Service Class
**File**: `app/services/email_service.py`

**Methods**:
- `EmailService.send_donor_welcome_email()` - Send to donors
- `EmailService.send_hospital_credentials_email()` - Send to hospitals

### Integration Points

**1. Donor Registration** (`app/routes/auth.py`)
```python
EmailService.send_donor_welcome_email(
    donor_email=email,
    donor_name=form.full_name.data,
    donor_id=donor_id
)
```

**2. Hospital Creation** (`app/routes/superadmin.py`)
```python
EmailService.send_hospital_credentials_email(
    hospital_email=email,
    hospital_name=hospital_name,
    hospital_id=hospital_id,
    username=username,
    password=password
)
```

---

## Best Practices

✅ **DO**:
- Use app passwords for Gmail (not account password)
- Test configuration before deploying
- Store credentials in .env, never in code
- Use TLS encryption (port 587)
- Monitor sending limits for your email provider

❌ **DON'T**:
- Hardcode email credentials
- Commit .env file to Git
- Use unsecured email protocols
- Ignore SMTP errors
- Exceed provider sending limits (e.g., Gmail: 500/day)

---

## Production Recommendations

For production deployments:

1. **Use SendGrid or AWS SES** instead of Gmail
2. **Enable rate limiting** to prevent abuse
3. **Log all email sends** for auditing
4. **Set up email templates** on provider side
5. **Monitor email delivery** rates
6. **Use environment-specific configs** (dev/prod)

---

## Support

For issues:
1. Check the troubleshooting section above
2. Review Flask-Mail documentation
3. Check email provider's SMTP settings
4. Test with simpler email first

---

**Last Updated**: May 2024
**BDMS Version**: 1.0
