"""
Email Service for BDMS
Handles sending emails with HTML templates for donors and hospital admins
"""
from flask_mail import Message
from flask import render_template_string, current_app
from app import mail
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Flask-Mail"""
    
    @staticmethod
    def _get_formatted_sender():
        """Get sender email with display name"""
        sender_name = current_app.config.get("MAIL_SENDER_NAME", "Blood Donor Management System")
        sender_email = current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@bdms.local")
        return (sender_name, sender_email)
    
    @staticmethod
    def send_donor_welcome_email(donor_email, donor_name, donor_id):
        """
        Send welcome email to newly registered donor with their unique ID
        
        Args:
            donor_email: Donor's email address
            donor_name: Donor's full name
            donor_id: Unique donor ID (e.g., BDMS-AB1234)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = f"Welcome to Blood Donor Management System - Your Donor ID: {donor_id}"
            html_body = render_template_string(
                DONOR_WELCOME_TEMPLATE,
                donor_name=donor_name,
                donor_id=donor_id
            )
            
            msg = Message(
                subject=subject,
                recipients=[donor_email],
                html=html_body,
                sender=EmailService._get_formatted_sender()
            )
            
            mail.send(msg)
            logger.info(f"Welcome email sent to donor: {donor_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send donor welcome email to {donor_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_hospital_credentials_email(hospital_email, hospital_name, hospital_id, username, password):
        """
        Send login credentials to newly created hospital admin
        
        Args:
            hospital_email: Hospital admin's email address
            hospital_name: Hospital name
            hospital_id: Unique hospital ID
            username: Hospital email (login ID)
            password: Temporary password
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = f"Your Hospital Admin Credentials - {hospital_name}"
            html_body = render_template_string(
                HOSPITAL_CREDENTIALS_TEMPLATE,
                hospital_name=hospital_name,
                hospital_id=hospital_id,
                username=username,
                password=password
            )
            
            msg = Message(
                subject=subject,
                recipients=[hospital_email],
                html=html_body,
                sender=EmailService._get_formatted_sender()
            )
            
            mail.send(msg)
            logger.info(f"Hospital credentials email sent to: {hospital_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send hospital credentials email to {hospital_email}: {str(e)}")
            return False


# ──────────────────────────────────────────────────────────────
# HTML EMAIL TEMPLATES
# ──────────────────────────────────────────────────────────────

DONOR_WELCOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to BDMS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .header {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            padding: 40px 20px;
            text-align: center;
            color: white;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .content {
            padding: 40px;
        }
        .greeting {
            font-size: 20px;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .message {
            color: #555;
            line-height: 1.6;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .donor-id-box {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
            color: white;
        }
        .donor-id-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        .donor-id-value {
            font-size: 32px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
        }
        .highlight {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            color: #856404;
            font-size: 13px;
        }
        .next-steps {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
        }
        .next-steps h3 {
            color: #333;
            font-size: 16px;
            margin-bottom: 12px;
        }
        .next-steps ol {
            margin-left: 20px;
            color: #555;
            font-size: 13px;
            line-height: 1.8;
        }
        .next-steps li {
            margin-bottom: 8px;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 12px 40px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            margin: 20px 0;
            transition: transform 0.2s;
        }
        .cta-button:hover {
            transform: translateY(-2px);
        }
        .footer {
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            border-top: 1px solid #e9ecef;
            font-size: 12px;
            color: #666;
            line-height: 1.6;
        }
        .footer a {
            color: #dc3545;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .divider {
            height: 2px;
            background: linear-gradient(to right, transparent, #ddd, transparent);
            margin: 25px 0;
        }
        .badge {
            display: inline-block;
            background: #dc3545;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="icon">🩸</div>
            <h1>Welcome to BDMS</h1>
            <p>Blood Donor Management System</p>
        </div>

        <!-- Content -->
        <div class="content">
            <div class="greeting">Hello {{ donor_name }}! 👋</div>
            
            <div class="message">
                Thank you for registering with the <strong>Blood Donor Management System</strong>. Your registration has been successful and we're excited to have you as part of our donor community.
            </div>

            <!-- Donor ID Card -->
            <div class="donor-id-box">
                <div class="donor-id-label">Your Unique Donor ID</div>
                <div class="donor-id-value">{{ donor_id }}</div>
            </div>

            <!-- Important Notice -->
            <div class="highlight">
                <strong>⚠️ Keep Your ID Safe:</strong> Your Donor ID is your unique identifier in our system. Please keep it secure and use it for all future logins and donations.
            </div>

            <!-- Divider -->
            <div class="divider"></div>

            <!-- Next Steps -->
            <div class="next-steps">
                <h3>📋 What's Next?</h3>
                <ol>
                    <li><strong>Verify Your Email:</strong> Check your email inbox to verify your account</li>
                    <li><strong>Complete Your Profile:</strong> Add your medical history and preferences</li>
                    <li><strong>Await Approval:</strong> Our admin team will review your registration</li>
                    <li><strong>Start Donating:</strong> Once approved, you can schedule your first donation</li>
                </ol>
            </div>

            <!-- Call to Action -->
            <center>
                <a href="https://blooddonor.local/auth/login" class="cta-button">Login to Your Account</a>
            </center>

            <!-- Donation Impact -->
            <div class="message" style="background: #e7f3ff; padding: 15px; border-radius: 6px; border-left: 4px solid #2196F3;">
                <strong>Did You Know?</strong> Every blood donation can save up to 3 lives. Your contribution is invaluable to our community. Thank you for being a life-saver! ❤️
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>
                <strong>Blood Donor Management System</strong><br>
                Connecting donors with hospitals to save lives
            </p>
            <div class="divider" style="margin: 15px 0; opacity: 0.5;"></div>
            <p>
                If you have any questions, please <a href="mailto:support@bdms.local">contact our support team</a><br>
                © 2024 BDMS. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""


HOSPITAL_CREDENTIALS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospital Admin Credentials</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .header {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            padding: 40px 20px;
            text-align: center;
            color: white;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .content {
            padding: 40px;
        }
        .hospital-name {
            font-size: 22px;
            color: #333;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .message {
            color: #555;
            line-height: 1.6;
            font-size: 14px;
            margin-bottom: 25px;
        }
        .credentials-box {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
        }
        .credentials-box h3 {
            color: #333;
            font-size: 14px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .credential-item {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e9ecef;
        }
        .credential-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        .credential-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .credential-value {
            background: white;
            border: 1px solid #dee2e6;
            padding: 10px 12px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            word-break: break-all;
        }
        .copy-note {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            font-style: italic;
        }
        .hospital-id-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            color: white;
        }
        .hospital-id-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        .hospital-id-value {
            font-size: 28px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
        }
        .security-warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            color: #856404;
            font-size: 13px;
            line-height: 1.6;
        }
        .security-warning strong {
            display: block;
            margin-bottom: 8px;
        }
        .next-steps {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            color: #2e7d32;
            font-size: 13px;
            line-height: 1.6;
        }
        .next-steps strong {
            display: block;
            margin-bottom: 8px;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            padding: 12px 40px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            margin: 20px 0;
            transition: transform 0.2s;
        }
        .cta-button:hover {
            transform: translateY(-2px);
        }
        .footer {
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            border-top: 1px solid #e9ecef;
            font-size: 12px;
            color: #666;
            line-height: 1.6;
        }
        .footer a {
            color: #007bff;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .divider {
            height: 2px;
            background: linear-gradient(to right, transparent, #ddd, transparent);
            margin: 25px 0;
        }
        .badge {
            display: inline-block;
            background: #dc3545;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="icon">🏥</div>
            <h1>Welcome Hospital Admin</h1>
            <p>Blood Donor Management System</p>
        </div>

        <!-- Content -->
        <div class="content">
            <div class="hospital-name">{{ hospital_name }}</div>
            
            <div class="message">
                Congratulations! Your hospital has been successfully registered in the <strong>Blood Donor Management System (BDMS)</strong>. Below are your admin login credentials to access the system.
            </div>

            <!-- Hospital ID Card -->
            <div class="hospital-id-box">
                <div class="hospital-id-label">Your Hospital ID</div>
                <div class="hospital-id-value">{{ hospital_id }}</div>
            </div>

            <!-- Credentials Box -->
            <div class="credentials-box">
                <h3>🔐 Login Credentials</h3>
                
                <div class="credential-item">
                    <div class="credential-label">Username / Email</div>
                    <div class="credential-value">{{ username }}</div>
                    <div class="copy-note">Use this email to login</div>
                </div>
                
                <div class="credential-item">
                    <div class="credential-label">Temporary Password</div>
                    <div class="credential-value">{{ password }}</div>
                    <div class="copy-note">⚠️ This is a temporary password. Change it on first login.</div>
                </div>
            </div>

            <!-- Security Warning -->
            <div class="security-warning">
                <strong>🔒 Security Important:</strong>
                <ul style="margin-left: 20px;">
                    <li>Store these credentials securely</li>
                    <li>Change the password immediately after first login</li>
                    <li>Do not share these credentials via email or chat</li>
                    <li>Use a strong, unique password for your account</li>
                </ul>
            </div>

            <!-- Next Steps -->
            <div class="next-steps">
                <strong>📋 Quick Start:</strong>
                <ol style="margin-left: 20px;">
                    <li>Visit the admin login page</li>
                    <li>Enter your email and temporary password</li>
                    <li>Change your password to a secure one</li>
                    <li>Set up your hospital inventory</li>
                    <li>Start managing blood donations</li>
                </ol>
            </div>

            <!-- Call to Action -->
            <center>
                <a href="https://blooddonor.local/auth/login" class="cta-button">Login Now</a>
            </center>

            <div class="message">
                If you have any questions or need assistance, please contact our support team. We're here to help you get the most out of BDMS!
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>
                <strong>Blood Donor Management System (BDMS)</strong><br>
                Connecting hospitals with donors to save lives
            </p>
            <div class="divider" style="margin: 15px 0; opacity: 0.5;"></div>
            <p>
                For support, contact: <a href="mailto:support@bdms.local">support@bdms.local</a><br>
                © 2024 BDMS. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
