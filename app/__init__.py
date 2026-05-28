from flask import Flask, redirect, url_for
from flask_login import current_user
from pymongo import MongoClient
from app.config import config
from app.extensions import login_manager, mail, csrf

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
    db.users.create_index("donor_id")
    db.users.create_index("email")
    db.users.create_index("phone")
    db.users.create_index([("hospital_id", 1), ("role", 1)])
    db.users.create_index([("role", 1), ("created_at", -1)])
    db.hospitals.create_index("hospital_id")
    db.hospitals.create_index("city")
    db.donation_requests.create_index([("donor_id", 1), ("created_at", -1)])
    db.donation_requests.create_index([("hospital_id", 1), ("created_at", -1)])
    db.donation_requests.create_index([("hospital_id", 1), ("status", 1), ("created_at", -1)])

    # ── Initialize Extensions ────────────────────────────
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # ── Home Route ───────────────────────────────────────
    @app.route("/")
    def index():
        """Home page that redirects based on authentication status."""
        if current_user.is_authenticated:
            # Redirect authenticated users to their dashboard
            if current_user.role == "donor":
                return redirect(url_for("donor.dashboard"))
            elif current_user.role in ["admin", "hospital_admin"]:
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == "superadmin":
                return redirect(url_for("superadmin.dashboard"))

        # Redirect unauthenticated users to landing page
        return redirect(url_for("auth.landing"))

    # ── Register Blueprints ──────────────────────────────
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

    return app
