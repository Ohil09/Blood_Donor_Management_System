from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta, timezone
from app import db
from app.decorators import donor_required

donor_bp = Blueprint("donor", __name__, url_prefix="/donor")


# ── Dashboard ────────────────────────────────────────────────
@donor_bp.route("/dashboard")
@login_required
@donor_required
def dashboard():
    """Show the donor's personal dashboard with eligibility status and stats."""
    try:
        donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    except InvalidId:
        flash("Session error. Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    # Calculate eligibility using configured interval (default: 56 days for whole blood)
    last_donation = donor.get("last_donation_date")
    is_eligible = True
    days_until_eligible = 0

    if last_donation:
        interval = current_app.config.get("WHOLE_BLOOD_INTERVAL", 56)
        next_eligible_date = last_donation + timedelta(days=interval)
        days_until_eligible = (next_eligible_date - datetime.now(timezone.utc)).days
        is_eligible = days_until_eligible <= 0

    donation_count = db.donations.count_documents({"donor_id": current_user.donor_id})
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
    """Display a read-only profile view for the authenticated donor."""
    try:
        donor = db.users.find_one({"_id": ObjectId(current_user.id)})
    except InvalidId:
        flash("Session error. Please log in again.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("donor/profile.html", donor=donor)


# ── History ──────────────────────────────────────────────────
@donor_bp.route("/history")
@login_required
@donor_required
def history():
    """Paginated donation history for the authenticated donor."""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    donations = list(
        db.donations.find({"donor_id": current_user.donor_id})
        .sort("donation_date", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    total_donations = db.donations.count_documents({"donor_id": current_user.donor_id})
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