from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    IntegerField,
    TextAreaField,
    DateField,
    SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length, ValidationError
from datetime import date

BLOOD_GROUP_CHOICES = [
    ("O+", "O+"), ("O-", "O-"),
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
]

COMPONENT_CHOICES = [
    ("whole_blood", "Whole Blood"),
    ("plasma", "Plasma"),
    ("platelets", "Platelets"),
]

URGENCY_CHOICES = [
    ("routine", "Routine"),
    ("urgent", "Urgent"),
    ("critical", "Critical"),
]


class BroadcastRequestForm(FlaskForm):
    """Form used by Hospital A to broadcast a blood need to other hospitals."""

    blood_group = SelectField(
        "Blood Group Required",
        choices=BLOOD_GROUP_CHOICES,
        validators=[DataRequired()],
    )
    component_type = SelectField(
        "Component Type",
        choices=COMPONENT_CHOICES,
        default="whole_blood",
        validators=[DataRequired()],
    )
    units_needed = IntegerField(
        "Units Needed",
        validators=[DataRequired(), NumberRange(min=1, max=500,
            message="Must be between 1 and 500 units")],
    )
    urgency = SelectField(
        "Urgency Level",
        choices=URGENCY_CHOICES,
        default="routine",
        validators=[DataRequired()],
    )
    required_by_date = DateField(
        "Required By Date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
    )
    notes = TextAreaField(
        "Additional Notes (optional)",
        validators=[Optional(), Length(max=500)],
    )
    submit = SubmitField("Broadcast Request")

    def validate_required_by_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("Required by date cannot be in the past.")


class SupplyOfferForm(FlaskForm):
    """Form used by Hospital B to respond with a supply offer."""

    units_offered = IntegerField(
        "Units You Can Supply",
        validators=[DataRequired(), NumberRange(min=1, max=500,
            message="Must be between 1 and 500 units")],
    )
    note = TextAreaField(
        "Note to Requesting Hospital (optional)",
        validators=[Optional(), Length(max=300)],
    )
    submit = SubmitField("Submit Offer")


class OfferActionForm(FlaskForm):
    """
    Minimal CSRF-protected form for accept / decline / cancel / complete
    POST actions (no visible fields needed — just the hidden CSRF token).
    """
    submit = SubmitField("Confirm")
