from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db
from app.forms.auth_forms import RegistrationForm, LoginForm
from app.models.user import User
from app.services.donor_id_service import generate_donor_id

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Register ────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        # Check duplicate email
        if db.users.find_one({"email": email}):
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        # Check duplicate phone
        if db.users.find_one({"phone": form.phone.data}):
            flash("Phone number already registered.", "danger")
            return redirect(url_for("auth.register"))

        donor_id = generate_donor_id()
        password_hash = generate_password_hash(form.password.data)

        # Insert donor WITHOUT hospital_id — admin assigns later
        db.users.insert_one({
            "donor_id": donor_id,
            "full_name": form.full_name.data,
            "email": email,
            "phone": form.phone.data,
            "age": form.age.data,
            "gender": form.gender.data,
            "blood_group": form.blood_group.data,
            "city": form.city.data,
            "password_hash": password_hash,
            "role": "donor",
            "hospital_id": None,
            "hospital_name": None,
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
            "last_donation_date": None,
        })

        flash(
            f"✅ Registration successful! Your Donor ID is {donor_id}. "
            "Please wait for admin approval to access full features.",
            "success",
        )
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
        password = form.password.data

        # Find user by donor_id OR email (email lookup is case-insensitive)
        doc = db.users.find_one({
            "$or": [
                {"donor_id": login_id},
                {"email": login_id.lower()},
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
    elif role in ("admin", "superadmin"):
        return redirect(url_for("admin.dashboard"))
    elif role == "hospital_admin":
        # Placeholder: hospital_admin dashboard not yet implemented.
        flash("Hospital admin portal is coming soon. Please contact the system administrator.", "info")
        return redirect(url_for("auth.login"))
    flash("Your account role is not recognised. Please contact support.", "warning")
    return redirect(url_for("auth.login"))