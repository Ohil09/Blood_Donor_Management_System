from flask import Flask
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

    # ── Initialize Extensions ────────────────────────────
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # ── Register Blueprints ──────────────────────────────
    # (Uncomment each one as you build them)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # from app.routes.donor      import donor_bp
    # from app.routes.admin      import admin_bp
    # from app.routes.superadmin import superadmin_bp
    # from app.routes.api        import api_bp
    # app.register_blueprint(donor_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(superadmin_bp)
    # app.register_blueprint(api_bp)

    return app