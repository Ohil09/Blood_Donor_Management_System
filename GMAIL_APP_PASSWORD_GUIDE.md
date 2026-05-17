# Gmail App Password Setup Guide

## ⚠️ Important: Gmail Account Requirements

Your Gmail account must have:
- ✅ **2-Factor Authentication (2FA) enabled**
- ✅ **Non-Google account access not restricted**

If you don't have 2FA, Gmail won't allow app passwords.

---

## 📋 Step-by-Step: Generate Gmail App Password

### Step 1: Enable 2-Factor Authentication (if not done)
```
1. Go to myaccount.google.com
2. Click "Security" (left menu)
3. Find "2-Step Verification"
4. Click "Enable"
5. Follow Google's setup wizard (SMS or authenticator app)
```

### Step 2: Generate App Password

**Method A: Via Google Account Website**

```
1. Go to myaccount.google.com
2. Click "Security" (left menu)
3. Scroll down to "2-Step Verification" section
4. Click "App passwords" (should appear after 2FA is enabled)
5. You may need to log in again
```

**Method B: Direct Link**
- Open: `https://myaccount.google.com/apppasswords`

### Step 3: Create Password for Your Application

```
1. Select "Mail" from first dropdown
2. Select "Windows Computer" from second dropdown
3. Click "Generate"
4. Google shows a 16-character password in format: xxxx xxxx xxxx xxxx
```

**Example:**
```
aebk cqkj mlpe ztrd
```

### Step 4: Copy the Password

```
1. Click "Copy" button
2. Password is now in your clipboard
3. This password ONLY appears once - save it somewhere safe
4. Click "Done"
```

---

## 🔧 Configure in BDMS

### Update Your `.env` File

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=aebk cqkj mlpe ztrd
MAIL_DEFAULT_SENDER=your_email@gmail.com
MAIL_SENDER_NAME=Smart Blood Management System
```

### Important Notes:
- ✅ Keep the **spaces** in the password (e.g., `aebk cqkj mlpe ztrd`)
- ✅ `MAIL_USERNAME` = your Gmail email
- ✅ `MAIL_DEFAULT_SENDER` = same as MAIL_USERNAME
- ✅ Do NOT use your Gmail account password
- ❌ Never commit `.env` to Git

---

## ✅ Test Your Configuration

### Run Email Test Script

```bash
cd D:\SBDMS
python test_email_config.py
```

**Expected Output:**
```
============================================================
📧 BDMS Email Configuration Test
============================================================

✓ Current Email Configuration:
  • Server: smtp.gmail.com
  • Port: 587
  • TLS: True
  • Username: your_email@gmail.com
  • Sender: your_email@gmail.com

✓ Credentials are configured

Enter test email address: your_test_email@gmail.com

⏳ Attempting to send test email...
✅ Success! Test email sent to your_test_email@gmail.com

📋 Checklist:
  ✓ Email configuration verified
  ✓ SMTP connection working
  ✓ Ready for production use
```

---

## 🐛 Troubleshooting

### ❌ "App passwords" Option Not Showing

**Problem:** You don't see "App passwords" in Security settings

**Solutions:**
1. Make sure 2-Factor Authentication is enabled
2. Wait a few minutes after enabling 2FA (sometimes takes time)
3. Log out and log back in to Google Account
4. Try using different browser (Chrome, Firefox, Edge)

### ❌ "SMTPAuthenticationError"

**Problem:** Email fails with authentication error

**Solutions:**
1. ✅ Verify password has NO typos
2. ✅ Keep spaces in password: `xxxx xxxx xxxx xxxx`
3. ✅ Use app password, NOT Gmail account password
4. ✅ Restart Flask app after updating `.env`
5. ✅ Check `MAIL_USERNAME` is correct email

### ❌ Password Showing as Hash (`$2a$...`)

**Problem:** Your `.env` still has bcrypt hash instead of actual password

**Solutions:**
1. Delete the old password value
2. Generate new app password from Google
3. Paste the 16-character password (with spaces)
4. Save `.env`
5. Restart app

---

## 🔐 Security Best Practices

1. **Use App Password, Not Account Password**
   - App password is ONLY for BDMS
   - Account password stays private
   - Can revoke app password anytime

2. **Keep `.env` Secure**
   - Never commit to Git
   - Never share with others
   - Store locally only

3. **Revoke Old Passwords**
   ```
   1. Go to myaccount.google.com/apppasswords
   2. Find "Mail - Windows Computer"
   3. Click trash icon to revoke
   4. Generate new one if needed
   ```

4. **Monitor Access**
   - Gmail shows which apps logged in recently
   - Check "Security" → "Your devices"

---

## 📊 Gmail App Password Format

```
Generated:  aebk cqkj mlpe ztrd    (with spaces - 19 chars total)
            ↑    ↑    ↑    ↑
          Group 1-4 (4 chars each)
```

- **Total length:** 19 characters (16 letters + 3 spaces)
- **Format:** Always 4 groups of 4 characters separated by spaces
- **Validity:** Permanent until you revoke it
- **Visibility:** Only shown once after generation

---

## ✨ Common Mistakes to Avoid

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| Account password | App password (16 char, 4 groups) |
| Remove spaces: `aebkcqkjmlpeztrd` | Keep spaces: `aebk cqkj mlpe ztrd` |
| Copy from somewhere else | Generate fresh from Google Account |
| Share `.env` file | Keep `.env` private |
| Use old/revoked password | Use current active password |

---

## 🎯 Quick Checklist

Before testing, verify:

- [ ] Gmail account has 2FA enabled
- [ ] App password generated (16 chars, 4 groups)
- [ ] `.env` updated with new app password
- [ ] Password format: `xxxx xxxx xxxx xxxx` (with spaces)
- [ ] `.env` NOT committed to Git
- [ ] Flask app restarted after updating `.env`
- [ ] `MAIL_USERNAME` is Gmail email address
- [ ] `MAIL_DEFAULT_SENDER` matches username

---

## 🚀 After Getting App Password

1. **Update `.env`** with your app password
2. **Restart Flask app** (`python run.py`)
3. **Test email** (`python test_email_config.py`)
4. **Register a donor** or **create a hospital** to see it work
5. **Check inbox** for welcome/credentials email

---

## 📚 References

- Google Account Security: https://myaccount.google.com/security
- App Passwords Help: https://support.google.com/accounts/answer/185833

---

**Status:** Once you have app password, email will work! ✅
