"""
Test Email Configuration Script
Run this to verify your SMTP settings are correct
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_email_config():
    """Test email configuration"""
    from app import create_app, mail
    from flask_mail import Message
    
    print("\n" + "="*60)
    print("📧 BDMS Email Configuration Test")
    print("="*60 + "\n")
    
    app = create_app()
    
    # Show configuration
    print("✓ Current Email Configuration:")
    print(f"  • Server: {app.config.get('MAIL_SERVER')}")
    print(f"  • Port: {app.config.get('MAIL_PORT')}")
    print(f"  • TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"  • Username: {app.config.get('MAIL_USERNAME', 'NOT SET')}")
    print(f"  • Sender: {app.config.get('MAIL_DEFAULT_SENDER', 'NOT SET')}")
    
    # Check if credentials are set
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("\n❌ Error: Email credentials not configured in .env")
        print("   Please set MAIL_USERNAME and MAIL_PASSWORD in .env file")
        return False
    
    print("\n✓ Credentials are configured\n")
    
    # Test sending
    test_email = input("Enter test email address: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address")
        return False
    
    print("\n⏳ Attempting to send test email...")
    
    try:
        with app.app_context():
            # Simple text email
            msg = Message(
                subject="🧪 BDMS Email Test - Configuration Success",
                recipients=[test_email],
                html="""
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; background: #f5f5f5; }
                        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                        .header { background: #28a745; color: white; padding: 20px; border-radius: 4px; text-align: center; }
                        .content { margin: 20px 0; }
                        .success { color: #28a745; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>✅ Email Configuration Successful!</h2>
                        </div>
                        <div class="content">
                            <p>Your BDMS email system is working correctly.</p>
                            <p>This is a test email sent from <strong>Blood Donor Management System</strong>.</p>
                            <hr>
                            <p><strong>Next Steps:</strong></p>
                            <ul>
                                <li>Test donor registration to receive welcome email</li>
                                <li>Create a hospital via superadmin to test hospital credentials email</li>
                                <li>Check your spam folder if emails don't arrive</li>
                            </ul>
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            mail.send(msg)
        
        print(f"✅ Success! Test email sent to {test_email}")
        print("\n📋 Checklist:")
        print("  ✓ Email configuration verified")
        print("  ✓ SMTP connection working")
        print("  ✓ Ready for production use")
        print("\n💡 Tip: Check your spam/junk folder if email doesn't appear in inbox")
        return True
        
    except Exception as e:
        print(f"\n❌ Error sending email: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("  1. Verify credentials in .env are correct")
        print("  2. For Gmail: Use app password (16 chars), not account password")
        print("  3. Check internet connection")
        print("  4. Check MAIL_SERVER and MAIL_PORT are correct")
        print(f"\n📝 Error Details: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        success = test_email_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
