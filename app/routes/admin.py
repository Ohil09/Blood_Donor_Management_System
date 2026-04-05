from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.inventory import Inventory
from app.services.inventory_service import InventoryService
from app.forms.inventory_forms import AddStockForm, DepleteStockForm, SearchInventoryForm
from datetime import datetime, timezone
from bson import ObjectId
from app.services.assignment_service import AssignmentService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Check role is admin ──────────────────────────────────────
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ["admin", "superadmin"]:
            flash("Access denied. Admin only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


# ── Admin Dashboard ──────────────────────────────────────────
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Main admin dashboard"""
    
    # Get admin's hospital_id from user document
    admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
    hospital_id = admin_user.get("hospital_id")
    
    if not hospital_id:
        flash("Hospital not assigned to your account.", "warning")
        return redirect(url_for("auth.login"))
    
    # Get inventory for this hospital
    inventory = Inventory.get_by_hospital(hospital_id, db)
    
    if not inventory:
        # Create new inventory if doesn't exist
        hospital_name = admin_user.get("hospital_name", "Unknown Hospital")
        inv_id = Inventory.init_for_hospital(hospital_id, hospital_name, db)
        doc = db.inventory.find_one({"_id": ObjectId(inv_id)})
        inventory = Inventory(doc)
    
    # Get low stock alert
    low_stock_alert = InventoryService.get_low_stock_alert(inventory)
    
    # Get donor count
    donor_count = db.users.count_documents({"hospital_id": hospital_id, "role": "donor"})
    
    # Get recent donations (last 5)
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
    
    admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
    hospital_id = admin_user.get("hospital_id")
    
    inventory = Inventory.get_by_hospital(hospital_id, db)
    
    if not inventory:
        flash("Inventory not initialized.", "danger")
        return redirect(url_for("admin.dashboard"))
    
    add_form = AddStockForm()
    deplete_form = DepleteStockForm()
    
    context = {
        "inventory": inventory,
        "add_form": add_form,
        "deplete_form": deplete_form,
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
        admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
        hospital_id = admin_user.get("hospital_id")
        
        inventory = Inventory.get_by_hospital(hospital_id, db)
        
        if not inventory:
            flash("Inventory not found.", "danger")
            return redirect(url_for("admin.inventory"))
        
        success, message = inventory.add_stock(
            form.blood_group.data,
            form.quantity.data,
            db
        )
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
    
    return redirect(url_for("admin.inventory"))


# ── Deplete Stock ────────────────────────────────────────────
@admin_bp.route("/inventory/deplete", methods=["POST"])
@login_required
@admin_required
def deplete_stock():
    """Deplete blood stock"""
    
    form = DepleteStockForm()
    
    if form.validate_on_submit():
        admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
        hospital_id = admin_user.get("hospital_id")
        
        inventory = Inventory.get_by_hospital(hospital_id, db)
        
        if not inventory:
            flash("Inventory not found.", "danger")
            return redirect(url_for("admin.inventory"))
        
        success, message = inventory.deplete_stock(
            form.blood_group.data,
            form.quantity.data,
            db
        )
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
    
    return redirect(url_for("admin.inventory"))


# ── Search Donors ────────────────────────────────────────────
@admin_bp.route("/search-donors", methods=["GET", "POST"])  # Add POST
@login_required
@admin_required
def search_donors():
    form = SearchInventoryForm()
    donors = []
    search_performed = False
    
    if form.validate_on_submit():  # works for both GET and POST
        search_performed = True
        blood_group = form.blood_group.data
        city = form.city.data
        only_eligible = form.only_eligible.data == "on"
        
        if not blood_group:
            flash("Please select a blood group.", "warning")
        else:
            donors = InventoryService.search_donors_by_blood_group(
                blood_group,
                city=city if city else None,
                only_eligible=only_eligible,
                db=db
            )
            
            # Format donor data for display
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
    """List all donors for this hospital"""
    
    admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
    hospital_id = admin_user.get("hospital_id")
    
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    donors = list(
        db.users.find({"hospital_id": hospital_id, "role": "donor"})
        .sort("created_at", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    
    total_donors = db.users.count_documents({"hospital_id": hospital_id, "role": "donor"})
    total_pages = (total_donors + per_page - 1) // per_page
    
    # Format donor data
    for donor in donors:
        donor["_id_str"] = str(donor["_id"])
        donor["days_until_eligible"] = InventoryService.get_days_until_eligible(donor)
        donor["is_eligible"] = InventoryService.is_donor_eligible(donor)
        donor["created_at_display"] = donor["created_at"].strftime("%d %b %Y")
    
    context = {
        "donors": donors,
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
    """View donors waiting for hospital assignment"""
    
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    # Get unassigned donors
    all_unassigned = AssignmentService.get_unassigned_donors(db)
    total_unassigned = len(all_unassigned)
    
    # Paginate
    unassigned = all_unassigned[(page - 1) * per_page : page * per_page]
    total_pages = (total_unassigned + per_page - 1) // per_page
    
    # Format
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
    """Assign donor to current admin's hospital"""
    
    admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
    hospital_id = admin_user.get("hospital_id")
    
    if not hospital_id:
        flash("Hospital not assigned to your account.", "danger")
        return redirect(url_for("admin.unassigned_donors"))
    
    success, message = AssignmentService.assign_donor_to_hospital(
        donor_id, hospital_id, db
    )
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for("admin.unassigned_donors"))


# ── Reassign Donor ───────────────────────────────────────────
@admin_bp.route("/reassign-donor/<donor_id>", methods=["POST"])
@login_required
@admin_required
def reassign_donor(donor_id):
    """Reassign donor from one hospital to another (admin only)"""
    
    admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
    hospital_id = admin_user.get("hospital_id")
    
    # Unassign first
    AssignmentService.unassign_donor(donor_id, db)
    
    # Reassign to current hospital
    success, message = AssignmentService.assign_donor_to_hospital(
        donor_id, hospital_id, db
    )
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for("admin.donors"))