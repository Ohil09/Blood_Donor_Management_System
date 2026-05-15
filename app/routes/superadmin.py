from flask import Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
import secrets
import string

from app import db
from app.forms.superadmin_forms import CreateHospitalForm
from app.services.hospital_id_service import generate_hospital_id
from app.services.email_service import EmailService

superadmin_bp = Blueprint("superadmin", __name__, url_prefix="/superadmin")

def superadmin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "superadmin":
            flash("Access denied. Super Admin only.", "danger")
            return render_template("auth/login.html")
        return f(*args, **kwargs)
    return decorated

def _generate_password(length=10):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

@superadmin_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
@superadmin_required
def dashboard():
    form = CreateHospitalForm()
    generated = None

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        existing = db.hospitals.find_one({"email": email})
        if existing:
            flash("Hospital with this email already exists.", "danger")
        else:
            hospital_id = generate_hospital_id()
            temp_password = _generate_password()

            # Create hospital record
            db.hospitals.insert_one({
                "hospital_id": hospital_id,
                "name": form.name.data.strip(),
                "address": form.address.data.strip(),
                "city": form.city.data.strip(),
                "phone": form.phone.data.strip(),
                "email": email,
                "created_at": datetime.now(timezone.utc),
            })

            # Create hospital admin user for login
            db.users.insert_one({
                "donor_id": None,
                "full_name": f"{form.name.data.strip()} Admin",
                "email": email,
                "phone": form.phone.data.strip(),
                "role": "hospital_admin",
                "hospital_id": hospital_id,
                "hospital_name": form.name.data.strip(),
                "password_hash": generate_password_hash(temp_password),
                "created_at": datetime.now(timezone.utc),
                "is_active": True,
                "city": form.city.data.strip(),
            })

            generated = {
                "hospital_id": hospital_id,
                "password": temp_password,
                "hospital_name": form.name.data.strip(),
                "email": email,
            }
            
            # Send credentials email to hospital admin
            email_sent = EmailService.send_hospital_credentials_email(
                hospital_email=email,
                hospital_name=form.name.data.strip(),
                hospital_id=hospital_id,
                username=email,
                password=temp_password
            )
            
            success_msg = "✅ Hospital created successfully!"
            if email_sent:
                success_msg += " Credentials email has been sent to the hospital admin."
            else:
                success_msg += " (Note: Credentials email could not be sent, but hospital is created.)"
            
            flash(success_msg, "success")
    elif request.method == "POST":
        flash("Please fix the highlighted form errors before generating Hospital ID.", "danger")

    hospitals = list(db.hospitals.find({}).sort("created_at", -1).limit(50))
    return render_template("superadmin/dashboard.html", form=form, generated=generated, hospitals=hospitals)
