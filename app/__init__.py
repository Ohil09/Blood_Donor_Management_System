from flask import Flask, app
from pymongo import MongoClient
from app.config import config
from app.extensions import login_manager, mail, csrf
from app.services.donation_service import DonationService

# Global db reference — imported by models and routes
db = None

def create_app(config_name="development"):
    app = Flask(__name__)

    # ── Load config ──────────────────────────────────────
    app.config.from_object(config[config_name])

    # ── Initialize MongoDB ───────────────────────────────
    global db
    client = MongoClient(app.config["MONGO_URI"])
    db = client[app.config["MONGO_DB_NAME"]]

    # ── Initialize Extensions ────────────────────────────
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # ── Register Blueprints ──────────────────────────────
    # (Uncomment each one as you build them)
    # Blueprints
    # Blueprints

    from app.routes.auth import auth_bp
    from app.routes.donor import donor_bp
    from app.routes.admin import admin_bp
    from app.routes.superadmin import superadmin_bp
    from app.services.donation_service import DonationService
    from app.services.exchange_service import ExchangeService
    DonationService.ensure_indexes(db)
    ExchangeService.ensure_indexes(db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(superadmin_bp)

    # from app.routes.donor      import donor_bp
    # from app.routes.admin      import admin_bp
    # from app.routes.superadmin import superadmin_bp
    # from app.routes.api        import api_bp
    # app.register_blueprint(donor_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(superadmin_bp)
    # app.register_blueprint(api_bp)

    return app
