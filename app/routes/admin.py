from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from app import db
from app.models.inventory import Inventory
from app.services.inventory_service import InventoryService
from app.forms.inventory_forms import AddStockForm, DepleteStockForm, SearchDonorForm
from app.decorators import admin_required
from app.services.assignment_service import AssignmentService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _get_admin_hospital_id():
    """Return the hospital_id stored on the current Flask-Login user object.

    Because ``hospital_id`` is loaded into ``current_user`` at login, there is
    no need to re-query the database on every admin page load.
    """
    return current_user.hospital_id


# ── Admin Dashboard ──────────────────────────────────────────
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Main admin dashboard"""

    hospital_id = _get_admin_hospital_id()

    if not hospital_id:
        flash("Hospital not assigned to your account.", "warning")
        return redirect(url_for("auth.login"))

    inventory = Inventory.get_by_hospital(hospital_id, db)

    if not inventory:
        hospital_name = current_user.hospital_name or "Unknown Hospital"
        inv_id = Inventory.init_for_hospital(hospital_id, hospital_name, db)
        try:
            doc = db.inventory.find_one({"_id": ObjectId(inv_id)})
        except InvalidId:
            flash("Could not initialise inventory.", "danger")
            return redirect(url_for("auth.login"))
        inventory = Inventory(doc)

    low_stock_alert = InventoryService.get_low_stock_alert(inventory)
    donor_count = db.users.count_documents({"hospital_id": hospital_id, "role": "donor"})

    recent_donations = list(
        db.donations.find({"hospital_id": hospital_id})
        .sort("donation_date", -1)
        .limit(5)
    )

    for donation in recent_donations:
        donation["donation_date_display"] = donation["donation_date"].strftime("%d %b %Y")

    context = {
        "inventory": inventory,
        "low_stock_alert": low_stock_alert,
        "donor_count": donor_count,
        "recent_donations": recent_donations,
    }

    return render_template("admin/dashboard.html", **context)


# ── Inventory Management ─────────────────────────────────────
@admin_bp.route("/inventory")
@login_required
@admin_required
def inventory():
    """View and manage blood inventory"""

    hospital_id = _get_admin_hospital_id()
    inv = Inventory.get_by_hospital(hospital_id, db)

    if not inv:
        flash("Inventory not initialized.", "danger")
        return redirect(url_for("admin.dashboard"))

    context = {
        "inventory": inv,
        "add_form": AddStockForm(),
        "deplete_form": DepleteStockForm(),
    }

    return render_template("admin/inventory.html", **context)


# ── Add Stock ────────────────────────────────────────────────
@admin_bp.route("/inventory/add", methods=["POST"])
@login_required
@admin_required
def add_stock():
    """Add blood stock"""

    form = AddStockForm()

    if form.validate_on_submit():
        hospital_id = _get_admin_hospital_id()
        inv = Inventory.get_by_hospital(hospital_id, db)

        if not inv:
            flash("Inventory not found.", "danger")
            return redirect(url_for("admin.inventory"))

        success, message = inv.add_stock(form.blood_group.data, form.quantity.data, db)
        flash(message, "success" if success else "danger")

    return redirect(url_for("admin.inventory"))


# ── Deplete Stock ────────────────────────────────────────────
@admin_bp.route("/inventory/deplete", methods=["POST"])
@login_required
@admin_required
def deplete_stock():
    """Deplete blood stock"""

    form = DepleteStockForm()

    if form.validate_on_submit():
        hospital_id = _get_admin_hospital_id()
        inv = Inventory.get_by_hospital(hospital_id, db)

        if not inv:
            flash("Inventory not found.", "danger")
            return redirect(url_for("admin.inventory"))

        success, message = inv.deplete_stock(form.blood_group.data, form.quantity.data, db)
        flash(message, "success" if success else "danger")

    return redirect(url_for("admin.inventory"))


# ── Search Donors ────────────────────────────────────────────
@admin_bp.route("/search-donors", methods=["GET", "POST"])
@login_required
@admin_required
def search_donors():
    """Search eligible donors by blood group and optional city filter."""
    form = SearchDonorForm()
    donors = []
    search_performed = False

    if form.validate_on_submit():
        search_performed = True
        blood_group = form.blood_group.data
        city = form.city.data.strip() if form.city.data else None
        only_eligible = form.only_eligible.data

        if not blood_group:
            flash("Please select a blood group.", "warning")
        else:
            donors = InventoryService.search_donors_by_blood_group(
                blood_group,
                city=city or None,
                only_eligible=only_eligible,
                db=db,
            )

            for donor in donors:
                donor["_id_str"] = str(donor["_id"])
                donor["days_until_eligible"] = InventoryService.get_days_until_eligible(donor)
                donor["is_eligible"] = InventoryService.is_donor_eligible(donor)

            flash(f"Found {len(donors)} donor(s).", "info")

    context = {
        "form": form,
        "donors": donors,
        "search_performed": search_performed,
    }

    return render_template("admin/search_donors.html", **context)


# ── Donor List ───────────────────────────────────────────────
@admin_bp.route("/donors")
@login_required
@admin_required
def donors():
    """List all donors assigned to this hospital (paginated)."""

    hospital_id = _get_admin_hospital_id()

    page = request.args.get("page", 1, type=int)
    per_page = 10

    donor_list = list(
        db.users.find({"hospital_id": hospital_id, "role": "donor"})
        .sort("created_at", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    total_donors = db.users.count_documents({"hospital_id": hospital_id, "role": "donor"})
    total_pages = (total_donors + per_page - 1) // per_page

    for donor in donor_list:
        donor["_id_str"] = str(donor["_id"])
        donor["days_until_eligible"] = InventoryService.get_days_until_eligible(donor)
        donor["is_eligible"] = InventoryService.is_donor_eligible(donor)
        donor["created_at_display"] = donor["created_at"].strftime("%d %b %Y")
        last_don = donor.get("last_donation_date")
        donor["last_donation_display"] = last_don.strftime("%d %b %Y") if last_don else "Never"

    context = {
        "donors": donor_list,
        "page": page,
        "total_pages": total_pages,
        "total_donors": total_donors,
    }

    return render_template("admin/donors.html", **context)


# ── Unassigned Donors ────────────────────────────────────────
@admin_bp.route("/unassigned-donors")
@login_required
@admin_required
def unassigned_donors():
    """View donors waiting for hospital assignment (DB-paginated)."""

    page = request.args.get("page", 1, type=int)
    per_page = 10

    total_unassigned = AssignmentService.count_unassigned_donors(db)
    total_pages = (total_unassigned + per_page - 1) // per_page

    unassigned = AssignmentService.get_unassigned_donors(
        db,
        skip=(page - 1) * per_page,
        limit=per_page,
    )

    for donor in unassigned:
        donor["_id_str"] = str(donor["_id"])
        donor["created_at_display"] = donor["created_at"].strftime("%d %b %Y")

    context = {
        "unassigned": unassigned,
        "page": page,
        "total_pages": total_pages,
        "total_unassigned": total_unassigned,
    }

    return render_template("admin/unassigned_donors.html", **context)


# ── Assign Donor to Hospital ─────────────────────────────────
@admin_bp.route("/assign-donor/<donor_id>", methods=["POST"])
@login_required
@admin_required
def assign_donor(donor_id):
    """Assign donor to the current admin's hospital."""

    hospital_id = _get_admin_hospital_id()

    if not hospital_id:
        flash("Hospital not assigned to your account.", "danger")
        return redirect(url_for("admin.unassigned_donors"))

    success, message = AssignmentService.assign_donor_to_hospital(donor_id, hospital_id, db)
    flash(message, "success" if success else "danger")

    return redirect(url_for("admin.unassigned_donors"))


# ── Reassign Donor ───────────────────────────────────────────
@admin_bp.route("/reassign-donor/<donor_id>", methods=["POST"])
@login_required
@admin_required
def reassign_donor(donor_id):
    """Reassign a donor from their current hospital to the admin's hospital."""

    hospital_id = _get_admin_hospital_id()

    # Unassign first, then reassign to current hospital
    AssignmentService.unassign_donor(donor_id, db)
    success, message = AssignmentService.assign_donor_to_hospital(donor_id, hospital_id, db)
    flash(message, "success" if success else "danger")

    return redirect(url_for("admin.donors"))