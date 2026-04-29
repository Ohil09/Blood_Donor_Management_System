from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    SelectField,
    TextAreaField,
    DateField,
    SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length


BLOOD_GROUP_CHOICES = [
    ("O+", "O+"),
    ("O-", "O-"),
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
]

BLOOD_GROUP_FILTER_CHOICES = [("", "-- All Blood Groups --")] + BLOOD_GROUP_CHOICES

COMPONENT_CHOICES = [
    ("whole_blood", "Whole Blood"),
    ("plasma", "Plasma"),
    ("platelets", "Platelets"),
]

URGENCY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("emergency", "Emergency"),
]

STATUS_FILTER_CHOICES = [
    ("", "-- All Statuses --"),
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("fulfilled", "Fulfilled"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
]


class BloodRequestForm(FlaskForm):
    """Form for creating a new blood donation request."""

    blood_group = SelectField(
        "Blood Group",
        choices=BLOOD_GROUP_CHOICES,
        validators=[DataRequired()],
    )
    component_type = SelectField(
        "Component Type",
        choices=COMPONENT_CHOICES,
        default="whole_blood",
    )
    units_required = IntegerField(
        "Units Required",
        validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1 unit")],
    )
    urgency = SelectField(
        "Urgency",
        choices=URGENCY_CHOICES,
        default="medium",
        validators=[DataRequired()],
    )
    required_by_date = DateField(
        "Required By Date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
    )
    patient_name = StringField(
        "Patient Name (optional)",
        validators=[Optional(), Length(max=120)],
    )
    notes = TextAreaField(
        "Notes (optional)",
        validators=[Optional(), Length(max=500)],
    )
    submit = SubmitField("Submit Request")


class RequestFilterForm(FlaskForm):
    """Filter form for listing blood requests."""

    status = SelectField("Status", choices=STATUS_FILTER_CHOICES)
    blood_group = SelectField("Blood Group", choices=BLOOD_GROUP_FILTER_CHOICES)
    submit = SubmitField("Filter")


class FulfillRequestForm(FlaskForm):
    """Form to mark a request as fulfilled."""

    units_provided = IntegerField(
        "Units Provided",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    submit = SubmitField("Mark as Fulfilled")


class RejectRequestForm(FlaskForm):
    """Form to reject a request with a reason."""

    reason = TextAreaField(
        "Reason for Rejection",
        validators=[Optional(), Length(max=300)],
    )
    submit = SubmitField("Reject Request")
