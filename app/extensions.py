from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect

login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Redirect to login page if @login_required fails
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.get_by_id(user_id)