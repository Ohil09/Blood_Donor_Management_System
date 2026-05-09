from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms.auth_forms import EditProfileForm
from datetime import datetime, timedelta, timezone
from bson import ObjectId

donor_bp = Blueprint("donor", __name__, url_prefix="/donor")


# ── Check role is donor ──────────────────────────────────────
def donor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "donor":
            flash("Access denied. Donor only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


# ── Dashboard ────────────────────────────────────────────────
@donor_bp.route("/dashboard")
@login_required
@donor_required
def dashboard():
    # Get donor document
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})

    # Calculate eligibility
    last_donation = donor.get("last_donation_date")
    is_eligible = True
    days_until_eligible = 0

    if last_donation:
        # 56 days for whole blood (simplest rule)
        next_eligible_date = last_donation + timedelta(days=56)
        days_until_eligible = (next_eligible_date - datetime.now(timezone.utc)).days
        is_eligible = days_until_eligible <= 0

    # Get donation count
    donation_count = db.donations.count_documents({"donor_id": current_user.donor_id})

    # Get last donation date for display
    last_donation_display = last_donation.strftime("%d %b %Y") if last_donation else "Never"

    context = {
        "donor": donor,
        "is_eligible": is_eligible,
        "days_until_eligible": max(0, days_until_eligible),
        "donation_count": donation_count,
        "last_donation_display": last_donation_display,
    }

    return render_template("donor/dashboard.html", **context)


# ── Profile ──────────────────────────────────────────────────
@donor_bp.route("/profile")
@login_required
@donor_required
def profile():
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("donor/profile.html", donor=donor)


# ── Edit Profile ──────────────────────────────────────────────
@donor_bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
@donor_required
def edit_profile():
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    form = EditProfileForm()

    if form.validate_on_submit():
        # Check if phone is already in use by another user
        existing_phone = db.users.find_one({
            "phone": form.phone.data,
            "_id": {"$ne": ObjectId(current_user.id)}
        })
        
        if existing_phone:
            flash("Phone number already registered.", "danger")
            return redirect(url_for("donor.edit_profile"))

        # Update user document
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "full_name": form.full_name.data,
                "age": form.age.data,
                "gender": form.gender.data,
                "blood_group": form.blood_group.data,
                "city": form.city.data,
                "phone": form.phone.data,
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        flash("Profile updated successfully!", "success")
        return redirect(url_for("donor.dashboard"))

    elif request.method == "GET":
        # Pre-fill form with current data
        form.full_name.data = donor.get("full_name", "")
        form.age.data = donor.get("age")
        form.gender.data = donor.get("gender", "")
        form.blood_group.data = donor.get("blood_group", "")
        form.city.data = donor.get("city", "")
        form.phone.data = donor.get("phone", "")

    return render_template("donor/edit_profile.html", form=form, donor=donor)


# ── History ──────────────────────────────────────────────────
@donor_bp.route("/history")
@login_required
@donor_required
def history():
    # Get all donations for this donor (paginated)
    page = request.args.get("page", 1, type=int)
    per_page = 10

    donations = list(
        db.donations.find({"donor_id": current_user.donor_id})
        .sort("donation_date", -1)  # newest first
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    total_donations = db.donations.count_documents({"donor_id": current_user.donor_id})
    total_pages = (total_donations + per_page - 1) // per_page

    # Format dates
    for donation in donations:
        donation["donation_date_display"] = donation["donation_date"].strftime("%d %b %Y, %I:%M %p")

    context = {
        "donations": donations,
        "page": page,
        "total_pages": total_pages,
        "total_donations": total_donations,
    }

    return render_template("donor/history.html", **context)