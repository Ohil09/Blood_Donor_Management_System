from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField,
    IntegerField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length,
    EqualTo, NumberRange
)

# BLOOD_GROUPS = [
#     ("", "-- Select Blood Group --"),
#     ("A+", "A+"), ("A-", "A-"),
#     ("B+", "B+"), ("B-", "B-"),
#     ("AB+", "AB+"), ("AB-", "AB-"),
#     ("O+", "O+"), ("O-", "O-"),
# ]

# GENDER_CHOICES = [
#     ("", "-- Select Gender --"),
#     ("Male", "Male"),
#     ("Female", "Female"),
#     ("Other", "Other"),
# ]

class RegistrationForm(FlaskForm):
    full_name = StringField("Full Name",
                    validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField("Age",
                    validators=[DataRequired(), NumberRange(min=18, max=65)])
    gender = SelectField("Gender",
                    choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
                    validators=[DataRequired()])
    blood_group = SelectField("Blood Group",
                    choices=[
                        ("O+", "O+"), ("O-", "O-"),
                        ("A+", "A+"), ("A-", "A-"),
                        ("B+", "B+"), ("B-", "B-"),
                        ("AB+", "AB+"), ("AB-", "AB-"),
                    ],
                    validators=[DataRequired()])
    city = StringField("City",
                    validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email",
                    validators=[DataRequired(), Email()])
    phone = StringField("Phone Number",
                    validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField("Password",
                    validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password",
                    validators=[EqualTo("password")])
    submit = SubmitField("Register as Donor")

class LoginForm(FlaskForm):
    login_id  = StringField("Donor ID / Admin ID",
                  validators=[DataRequired()])
    password  = PasswordField("Password",
                  validators=[DataRequired()])
    submit    = SubmitField("Login")