from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db
from app.forms.auth_forms import RegistrationForm, LoginForm
from app.models.user import User
from app.services.donor_id_service import generate_donor_id
from app.services.email_service import EmailService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Home / Landing Page ─────────────────────────────────────
@auth_bp.route("/", methods=["GET"])
def landing():
    """Display the landing page with login/register options."""
    if current_user.is_authenticated:
        # Redirect authenticated users to their dashboard
        if current_user.role == "donor":
            return redirect(url_for("donor.dashboard"))
        elif current_user.role in ["admin", "hospital_admin"]:
            return redirect(url_for("admin.dashboard"))
        elif current_user.role == "superadmin":
            return redirect(url_for("superadmin.dashboard"))

    return render_template("landing.html")


# ── Register ────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        phone = form.phone.data.strip()

        # Check duplicate email
        existing_email = db.users.find_one({"email": email})
        if existing_email:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))
        
        # Check duplicate phone
        existing_phone = db.users.find_one({"phone": phone})
        if existing_phone:
            flash("Phone number already registered.", "danger")
            return redirect(url_for("auth.register"))
        
        # Generate donor ID
        donor_id = generate_donor_id()
        
        # Hash password
        password_hash = generate_password_hash(form.password.data)
        
        # Insert donor WITHOUT hospital_id
        db.users.insert_one({
            "donor_id": donor_id,
            "full_name": form.full_name.data,
            "email": email,
            "phone": phone,
            "age": form.age.data,
            "gender": form.gender.data,
            "blood_group": form.blood_group.data,
            "city": form.city.data,
            "password_hash": password_hash,
            "role": "donor",
            "hospital_id": None,  #  NOT ASSIGNED YET
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
            "last_donation_date": None,
            "next_eligible_date": None,
            "donation_count": 0,
        })
        
        # Send welcome email with donor ID
        email_sent = EmailService.send_donor_welcome_email(
            donor_email=email,
            donor_name=form.full_name.data,
            donor_id=donor_id
        )
        
        success_msg = f"✅ Registration successful! Your Donor ID is {donor_id}."
        if email_sent:
            success_msg += " A welcome email has been sent to your inbox."
        else:
            success_msg += " (Note: Welcome email could not be sent, but your registration is complete.)"
        success_msg += " Please wait for admin approval to access full features."
        
        flash(success_msg, "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html", form=form)


# ── Login ────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    form = LoginForm()

    if form.validate_on_submit():
        login_id = form.login_id.data.strip()
        login_id_upper = login_id.upper()
        login_id_lower = login_id.lower()
        password = form.password.data

        # Find user by donor_id, email, OR hospital_id for admins
        doc = db.users.find_one({
            "$or": [
            {"donor_id": login_id_upper},
            {"email": login_id_lower},
            {"hospital_id": login_id_upper, "role": {"$in": ["admin", "hospital_admin", "superadmin"]}}
        ]
    })
        if not doc or not check_password_hash(doc["password_hash"], password):
            flash("Invalid credentials. Please try again.", "danger")
            return render_template("auth/login.html", form=form)

        user = User(doc)
        login_user(user)
        flash(f"Welcome back, {user.full_name}!", "success")
        return _redirect_by_role(user.role)

    return render_template("auth/login.html", form=form)


# ── Logout ───────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ── Helper ───────────────────────────────────────────────────
def _redirect_by_role(role):
    if role == "donor":
        return redirect(url_for("donor.dashboard"))
    elif role == "superadmin":
        return redirect(url_for("superadmin.dashboard"))
    elif role in ["admin", "hospital_admin"]:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("auth.login"))
