from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField,
    IntegerField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length,
    EqualTo, NumberRange
)

BLOOD_GROUPS = [
    ("", "-- Select Blood Group --"),
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
    ("O+", "O+"), ("O-", "O-"),
]

GENDER_CHOICES = [
    ("", "-- Select Gender --"),
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
]

class RegistrationForm(FlaskForm):
    full_name   = StringField("Full Name",
                    validators=[DataRequired(), Length(min=2, max=100)])
    age         = IntegerField("Age",
                    validators=[DataRequired(), NumberRange(min=18, max=65,
                    message="Donor age must be between 18 and 65.")])
    gender      = SelectField("Gender",
                    choices=GENDER_CHOICES, validators=[DataRequired()])
    phone       = StringField("Phone Number",
                    validators=[DataRequired(), Length(min=10, max=15)])
    email       = StringField("Email Address",
                    validators=[DataRequired(), Email()])
    city        = StringField("City",
                    validators=[DataRequired(), Length(min=2, max=100)])
    blood_group = SelectField("Blood Group",
                    choices=BLOOD_GROUPS, validators=[DataRequired()])
    password    = PasswordField("Password",
                    validators=[DataRequired(), Length(min=6,
                    message="Password must be at least 6 characters.")])
    confirm     = PasswordField("Confirm Password",
                    validators=[DataRequired(),
                    EqualTo("password", message="Passwords must match.")])
    submit      = SubmitField("Register as Donor")


class LoginForm(FlaskForm):
    login_id  = StringField("Donor ID / Admin ID",
                  validators=[DataRequired()])
    password  = PasswordField("Password",
                  validators=[DataRequired()])
    submit    = SubmitField("Login")