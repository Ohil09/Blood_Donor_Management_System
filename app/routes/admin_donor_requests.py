# ── Donor Donation Requests ──────────────────────────────────
# These routes handle donation requests from donors to hospitals


def register_donor_request_routes(admin_bp, db, ObjectId, render_template, redirect, url_for, flash, request, login_required, current_user, datetime, timezone, Inventory):
    """Register donation request routes to admin blueprint"""
    
    @admin_bp.route("/donor-requests")
    @login_required
    def donor_requests_list():
        """View all donation requests for this hospital from donors"""
        from app.utils.auth_utils import admin_required
        
        @admin_required
        def view_list():
            from app.models.donation_request import DonationRequest
            
            admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
            hospital_id = admin_user.get("hospital_id")
            
            if not hospital_id:
                flash("Hospital not assigned to your account.", "warning")
                return redirect(url_for("admin.dashboard"))

            page = request.args.get("page", 1, type=int)
            status_filter = request.args.get("status", "", type=str)

            query = {"hospital_id": hospital_id}
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
            }

            return render_template("admin/donor_requests_list.html", **context)
        
        return view_list()
    
    
    @admin_bp.route("/donor-requests/<request_id>", methods=["GET", "POST"])
    @login_required
    def donor_request_detail(request_id):
        """View and accept/reject a specific donation request"""
        from app.utils.auth_utils import admin_required
        from app.forms.donation_forms import DonationRequestActionForm
        from app.models.donation_request import DonationRequest
        
        @admin_required
        def handle_request():
            admin_user = db.users.find_one({"_id": ObjectId(current_user.id)})
            hospital_id = admin_user.get("hospital_id")
            
            if not hospital_id:
                flash("Hospital not assigned to your account.", "warning")
                return redirect(url_for("admin.dashboard"))

            try:
                req_doc = db.donation_requests.find_one({
                    "_id": ObjectId(request_id),
                    "hospital_id": hospital_id
                })
            except:
                req_doc = None

            if not req_doc:
                flash("❌ Donation request not found.", "danger")
                return redirect(url_for("admin.donor_requests_list"))

            donor_request = DonationRequest(req_doc)
            form = DonationRequestActionForm()

            if form.validate_on_submit():
                action = form.action.data
                
                if donor_request.status != "pending":
                    flash("❌ This request has already been processed.", "warning")
                    return redirect(url_for("admin.donor_requests_list"))

                if action == "accept":
                    # Update status
                    db.donation_requests.update_one(
                        {"_id": ObjectId(request_id)},
                        {
                            "$set": {
                                "status": "accepted",
                                "accepted_at": datetime.now(timezone.utc),
                                "accepted_by": str(current_user.id),
                                "updated_at": datetime.now(timezone.utc)
                            },
                            "$push": {
                                "audit": {
                                    "action": "accepted",
                                    "actor_id": str(current_user.id),
                                    "timestamp": datetime.now(timezone.utc),
                                    "note": f"Accepted by {admin_user.get('full_name')}"
                                }
                            }
                        }
                    )
                    
                    # Update inventory - add units to blood group stock
                    inventory = Inventory.get_by_hospital(hospital_id, db)
                    if inventory:
                        success, msg = inventory.add_stock(
                            donor_request.blood_group,
                            donor_request.units_offered,
                            db
                        )

                    flash(f"✅ Donation request accepted! {donor_request.units_offered} units of {donor_request.blood_group} added to inventory.", "success")
                    
                elif action == "reject":
                    # Update status
                    db.donation_requests.update_one(
                        {"_id": ObjectId(request_id)},
                        {
                            "$set": {
                                "status": "rejected",
                                "rejection_reason": form.rejection_reason.data,
                                "updated_at": datetime.now(timezone.utc)
                            },
                            "$push": {
                                "audit": {
                                    "action": "rejected",
                                    "actor_id": str(current_user.id),
                                    "timestamp": datetime.now(timezone.utc),
                                    "note": form.rejection_reason.data or "No reason provided"
                                }
                            }
                        }
                    )
                    
                    flash("✅ Donation request rejected.", "warning")

                return redirect(url_for("admin.donor_requests_list"))

            context = {
                "donor_request": donor_request,
                "form": form,
                "created_display": DonationRequest.format_dt(donor_request.created_at),
                "accepted_display": DonationRequest.format_dt(donor_request.accepted_at) if donor_request.accepted_at else "-",
                "preferred_display": DonationRequest.format_date(donor_request.preferred_date) if donor_request.preferred_date else "-",
            }

            return render_template("admin/donor_request_detail.html", **context)
        
        return handle_request()
