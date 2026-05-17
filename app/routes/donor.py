from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms.auth_forms import EditProfileForm
from datetime import datetime, timedelta, timezone
from bson import ObjectId

donor_bp = Blueprint("donor", __name__, url_prefix="/donor")


def _to_utc_aware(value):
    if not value or not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    last_donation = _to_utc_aware(donor.get("last_donation_date"))
    next_eligible = _to_utc_aware(donor.get("next_eligible_date"))

    is_eligible = True
    days_until_eligible = 0
    now_utc = datetime.now(timezone.utc)

    if next_eligible:
        days_until_eligible = (next_eligible - now_utc).days
        is_eligible = days_until_eligible <= 0
    elif last_donation:
        next_eligible = last_donation + timedelta(days=56)
        days_until_eligible = (next_eligible - now_utc).days
        is_eligible = days_until_eligible <= 0

    last_donation_display = last_donation.strftime("%d %b %Y") if last_donation else "Never"
    next_eligible_display = next_eligible.strftime("%d %b %Y") if next_eligible else "Now"

    donor_id = donor.get("donor_id")
    donation_count = db.donations.count_documents({"donor_id": donor_id}) if donor_id else 0

    recent_donations = list(
        db.donations.find({"donor_id": donor_id} if donor_id else {})
        .sort("donation_date", -1)
        .limit(5)
    ) if donor_id else []

    for donation in recent_donations:
        donation["donation_date_display"] = donation["donation_date"].strftime("%d %b %Y")

    context = {
        "donor": donor,
        "is_eligible": is_eligible,
        "days_until_eligible": max(0, days_until_eligible),
        "donation_count": donation_count,
        "last_donation_display": last_donation_display,
        "next_eligible_display": next_eligible_display,
        "recent_donations": recent_donations,
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
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    donor_id = donor.get("donor_id")

    page = request.args.get("page", 1, type=int)
    per_page = 10

    if not donor_id:
        context = {
            "donations": [],
            "page": 1,
            "total_pages": 0,
            "total_donations": 0,
        }
        return render_template("donor/history.html", **context)

    donations = list(
        db.donations.find({"donor_id": donor_id})
        .sort("donation_date", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    total_donations = db.donations.count_documents({"donor_id": donor_id})
    total_pages = (total_donations + per_page - 1) // per_page

    for donation in donations:
        donation["donation_date_display"] = donation["donation_date"].strftime("%d %b %Y, %I:%M %p")

    context = {
        "donations": donations,
        "page": page,
        "total_pages": total_pages,
        "total_donations": total_donations,
    }

    return render_template("donor/history.html", **context)


# ── Change Password ──────────────────────────────────────────
@donor_bp.route("/change-password", methods=["GET", "POST"])
@login_required
@donor_required
def change_password():
    from app.forms.auth_forms import ChangePasswordForm
    from werkzeug.security import check_password_hash, generate_password_hash

    form = ChangePasswordForm()

    if form.validate_on_submit():
        donor = db.users.find_one({"_id": ObjectId(current_user.id)})
        
        # Verify current password
        if not check_password_hash(donor.get("password_hash", ""), form.old_password.data):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("donor.change_password"))
        
        # Update password
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "password_hash": generate_password_hash(form.new_password.data),
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        flash("✅ Password changed successfully!", "success")
        return redirect(url_for("donor.dashboard"))

    return render_template("donor/change_password.html", form=form)


# ── Search Hospitals ─────────────────────────────────────────
@donor_bp.route("/find-hospitals", methods=["GET"])
@login_required
@donor_required
def find_hospitals():
    """Search for hospitals by city or view all hospitals"""
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    search_city = request.args.get("city", "").strip()
    
    query = {}
    if search_city:
        query = {"city": {"$regex": search_city, "$options": "i"}}
    
    hospitals = list(db.hospitals.find(query).sort("city", 1).limit(50))
    
    context = {
        "hospitals": hospitals,
        "search_city": search_city,
        "donor": donor,
    }

    return render_template("donor/find_hospitals.html", **context)


# ── Donation Request - Create ────────────────────────────────
@donor_bp.route("/donation-request/new", methods=["GET", "POST"])
@login_required
@donor_required
def donation_request_new():
    from app.forms.donation_forms import DonationRequestForm

    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    donor_id = donor.get("donor_id")
    
    # Check if donor is eligible
    is_eligible = True
    next_eligible = _to_utc_aware(donor.get("next_eligible_date"))
    last_donation = _to_utc_aware(donor.get("last_donation_date"))
    now_utc = datetime.now(timezone.utc)
    
    if next_eligible:
        is_eligible = next_eligible <= now_utc
    elif last_donation:
        next_eligible = last_donation + timedelta(days=56)
        is_eligible = next_eligible <= now_utc

    if not is_eligible:
        flash("❌ You are not eligible to donate at this time.", "danger")
        return redirect(url_for("donor.dashboard"))

    form = DonationRequestForm()
    
    # Populate hospital choices
    hospitals = list(db.hospitals.find({}).sort("name", 1))
    form.hospital_id.choices = [
        (h["hospital_id"], f"{h['name']} - {h['city']}")
        for h in hospitals
        if h.get("hospital_id") and h.get("name")
    ]
    if request.method == "GET":
        requested_hospital_id = request.args.get("hospital_id")
        if requested_hospital_id and any(
            choice[0] == requested_hospital_id for choice in form.hospital_id.choices
        ):
            form.hospital_id.data = requested_hospital_id

    if form.validate_on_submit():
        # Check if already has pending request at same hospital
        existing = db.donation_requests.find_one({
            "donor_id": donor_id,
            "hospital_id": form.hospital_id.data,
            "status": {"$in": ["pending", "accepted"]}
        })
        
        if existing:
            flash("❌ You already have a pending or accepted request at this hospital.", "warning")
            return redirect(url_for("donor.donation_request_new"))

        # Create donation request
        preferred_date = None
        if form.preferred_date.data:
            try:
                preferred_date = datetime.strptime(form.preferred_date.data, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                flash("Preferred date must be in YYYY-MM-DD format.", "danger")
                return render_template("donor/donation_request_new.html", form=form, donor=donor)

        hospital = db.hospitals.find_one({"hospital_id": form.hospital_id.data})
        
        doc = {
            "donor_id": donor_id,
            "donor_user_id": ObjectId(current_user.id),
            "donor_name": donor.get("full_name"),
            "blood_group": donor.get("blood_group"),
            "hospital_id": form.hospital_id.data,
            "hospital_name": hospital.get("name") if hospital else "Unknown Hospital",
            "units_offered": form.units_offered.data,
            "urgency_level": form.urgency_level.data,
            "preferred_date": preferred_date,
            "additional_notes": form.additional_notes.data,
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "accepted_at": None,
            "accepted_by": None,
            "rejection_reason": "",
            "audit": [{
                "action": "created",
                "actor_id": str(current_user.id),
                "timestamp": datetime.now(timezone.utc),
                "note": f"Donor {donor_id} created request"
            }]
        }
        
        result = db.donation_requests.insert_one(doc)
        
        flash("✅ Donation request submitted successfully! Hospital will review it shortly.", "success")
        return redirect(url_for("donor.donation_requests_list"))

    return render_template("donor/donation_request_new.html", form=form, donor=donor)


# ── Donation Requests - List ─────────────────────────────────
@donor_bp.route("/donation-requests")
@login_required
@donor_required
def donation_requests_list():
    """View all donation requests for the logged-in donor"""
    donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    donor_id = donor.get("donor_id")

    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "", type=str)

    query = {"donor_id": donor_id}
    if status_filter and status_filter in ["pending", "accepted", "rejected", "cancelled", "fulfilled"]:
        query["status"] = status_filter

    requests = list(
        db.donation_requests.find(query)
        .sort("created_at", -1)
        .skip((page - 1) * 10)
        .limit(10)
    )

    total_requests = db.donation_requests.count_documents(query)
    total_pages = (total_requests + 9) // 10

    # Import model for formatting
    from app.models.donation_request import DonationRequest
    
    formatted_requests = []
    for req in requests:
        dr = DonationRequest(req)
        formatted_requests.append({
            "doc": req,
            "model": dr,
            "created_display": DonationRequest.format_dt(dr.created_at),
            "accepted_display": DonationRequest.format_dt(dr.accepted_at) if dr.accepted_at else "-",
            "preferred_display": DonationRequest.format_date(dr.preferred_date) if dr.preferred_date else "-",
        })

    context = {
        "requests": formatted_requests,
        "page": page,
        "total_pages": total_pages,
        "total_requests": total_requests,
        "status_filter": status_filter,
        "donor": donor,
    }

    return render_template("donor/donation_requests_list.html", **context)
