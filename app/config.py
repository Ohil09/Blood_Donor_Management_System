import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file into os.environ

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-key-change-me")
    FLASK_ENV  = os.environ.get("FLASK_ENV", "development")

    # MongoDB
    MONGO_URI    = os.environ.get("MONGO_URI", "mongodb://localhost:27017/bdms_dev")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "bdms_dev")

    # Flask-Mail
    MAIL_SERVER         = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT           = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS        = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME       = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD       = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Twilio (optional)
    TWILIO_ACCOUNT_SID  = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN   = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER  = os.environ.get("TWILIO_FROM_NUMBER")

    # Business Rules
    LOW_STOCK_THRESHOLD    = int(os.environ.get("LOW_STOCK_THRESHOLD", 5))
    WHOLE_BLOOD_INTERVAL   = int(os.environ.get("WHOLE_BLOOD_INTERVAL", 56))
    PLATELET_INTERVAL      = int(os.environ.get("PLATELET_INTERVAL", 7))
    PLASMA_INTERVAL        = int(os.environ.get("PLASMA_INTERVAL", 28))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Active config selector
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig
}