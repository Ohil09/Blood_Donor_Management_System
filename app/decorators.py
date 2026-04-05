from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def donor_required(f):
    """Restrict a view to authenticated donors only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "donor":
            flash("Access denied. Donor only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Restrict a view to authenticated admin or superadmin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ["admin", "superadmin"]:
            flash("Access denied. Admin only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
