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
        # Duplicate check
        if db.users.find_one({"email": form.email.data}):
            flash("Email already registered. Please login.", "danger")
            return render_template("auth/register.html", form=form)

        if db.users.find_one({"phone": form.phone.data}):
            flash("Phone number already registered.", "danger")
            return render_template("auth/register.html", form=form)

        # Generate unique Donor ID
        donor_id = generate_donor_id()

        # Insert into MongoDB
        db.users.insert_one({
            "donor_id":      donor_id,
            "full_name":     form.full_name.data,
            "age":           form.age.data,
            "gender":        form.gender.data,
            "phone":         form.phone.data,
            "email":         form.email.data.lower(),
            "city":          form.city.data,
            "blood_group":   form.blood_group.data,
            "password_hash": generate_password_hash(form.password.data),
            "role":          "donor",
            "is_active":     True,
            "created_at":    datetime.now(timezone.utc),
        })

        flash(f"Registration successful! Your Donor ID is: {donor_id} — Save this for login.", "success")
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

        # Find user by donor_id OR email
        doc = db.users.find_one({
            "$or": [
                {"donor_id": login_id},
                {"email":    login_id.lower()}
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
        return redirect(url_for("auth.login"))   # temp until donor bp exists
    elif role == "hospital_admin":
        return redirect(url_for("auth.login"))   # temp until admin bp exists
    elif role == "superadmin":
        return redirect(url_for("auth.login"))   # temp until superadmin bp exists
    return redirect(url_for("auth.login"))