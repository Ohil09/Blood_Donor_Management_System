# 🚀 Email Feature Quick Start Guide

## What's New?
Your BDMS now automatically sends beautiful HTML emails when:
1. **A donor registers** → Welcome email with Donor ID
2. **A hospital is created** → Admin credentials email

## 📋 Quick Setup (5 minutes)

### Step 1: Update .env File
Open `.env` in the project root and fill in the email fields:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com        # Your Gmail address
MAIL_PASSWORD=xxxx xxxx xxxx xxxx          # Your App Password (not Gmail password!)
MAIL_DEFAULT_SENDER=your_email@gmail.com  # Usually same as MAIL_USERNAME
```

### Step 2: Get Gmail App Password
**For Gmail users only:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Windows Computer**
3. Copy the 16-character password Google generates
4. Paste it in `.env` as `MAIL_PASSWORD` (keep the spaces)

⚠️ **Important**: Do NOT use your Gmail password. Use the App Password instead.

### Step 3: Test Configuration
```bash
python test_email_config.py
```
This will send a test email and verify everything works.

### Step 4: Done! ✅
Restart your app and test:
- Register a donor → Check email for welcome message
- Create a hospital (as superadmin) → Check email for credentials

---

## 📧 Email Templates

### Donor Welcome Email
- Beautiful gradient header with blood donation icon
- Unique Donor ID in large, easy-to-read format
- Security reminder to keep ID safe
- Next steps checklist
- Donation impact message

### Hospital Admin Email
- Professional blue gradient design
- Hospital ID
- Login username and temporary password
- Security warnings
- Quick start guide

---

## 🔧 Using Different Email Providers

### Outlook/Hotmail
```
MAIL_SERVER=smtp.outlook.com
MAIL_PORT=587
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
```

### SendGrid (Recommended for Production)
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your_api_key_here
```

See [EMAIL_SETUP.md](./EMAIL_SETUP.md) for complete guide.

---

## ✅ Verification Checklist

After setup, verify:
- [ ] `.env` file updated with email credentials
- [ ] Test email sent successfully via `test_email_config.py`
- [ ] Can see test email in inbox (check spam folder too)
- [ ] Registered a test donor account
- [ ] Received welcome email at registration email
- [ ] Created test hospital (as superadmin)
- [ ] Received credentials email at hospital email

---

## 🐛 Troubleshooting

### Emails not being sent?
1. Run `test_email_config.py` to verify configuration
2. Check that `.env` file has correct values (no typos)
3. For Gmail: Ensure you're using App Password, not Gmail password
4. Check spam/junk folder

### "SMTPAuthenticationError"?
- Verify MAIL_USERNAME is correct
- For Gmail: Use 16-char App Password
- No leading/trailing spaces

### Email won't connect?
- Check internet connection
- Verify MAIL_SERVER spelling
- Try MAIL_PORT=465 instead of 587

See [EMAIL_SETUP.md](./EMAIL_SETUP.md) for complete troubleshooting.

---

## 📁 Files Reference

- **Email Service**: `app/services/email_service.py`
  - `EmailService.send_donor_welcome_email()`
  - `EmailService.send_hospital_credentials_email()`

- **Integration**:
  - Donor registration: `app/routes/auth.py`
  - Hospital creation: `app/routes/superadmin.py`

- **Configuration**:
  - Environment variables: `.env`
  - App config: `app/config.py`

- **Documentation**:
  - Full setup guide: `EMAIL_SETUP.md`
  - Test script: `test_email_config.py`

---

## 💡 Tips

1. **Development**: Use Gmail with app password for easy setup
2. **Production**: Switch to SendGrid or AWS SES for reliability
3. **Testing**: Use `test_email_config.py` before each major change
4. **Monitoring**: Check email logs if deliverability issues occur
5. **Rate Limiting**: Gmail allows ~500 emails/day. SendGrid has higher limits.

---

## 🎯 Features

✨ **Beautiful HTML Templates**
- Professional gradient designs
- Mobile-responsive
- Clear call-to-action buttons
- Security best practices included

🔐 **Security**
- Credentials stored in .env, never in code
- TLS encryption enabled
- Password security guidelines in emails
- Temporary passwords for new accounts

🚀 **Automatic**
- Emails send automatically after registration/creation
- No manual intervention needed
- Graceful error handling

📱 **Professional**
- Brand-consistent design
- Clear, actionable information
- Impact messaging (blood donation facts)
- Support contact information

---

## 🆘 Need Help?

1. Check [EMAIL_SETUP.md](./EMAIL_SETUP.md) for detailed guide
2. Run `test_email_config.py` to debug
3. Review Flask-Mail documentation
4. Check email provider's SMTP settings

---

**Status**: ✅ Ready to use
**Last Updated**: May 2024
**BDMS Version**: 1.0+
