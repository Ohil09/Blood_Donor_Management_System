from datetime import date
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, TextAreaField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, ValidationError

BLOOD_GROUP_CHOICES = [
    ("O+", "O+"), ("O-", "O-"),
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
]

URGENCY_CHOICES = [
    ("routine", "Routine"),
    ("critical", "Critical"),
]


class CreateExchangeRequestForm(FlaskForm):
    target_hospital_id = SelectField("Target Hospital", validators=[DataRequired()], choices=[])
    blood_group = SelectField("Required Blood Group", choices=BLOOD_GROUP_CHOICES, validators=[DataRequired()])
    units_required = IntegerField("Units Required", validators=[DataRequired(), NumberRange(min=1, max=100)])
    urgency = SelectField("Urgency", choices=URGENCY_CHOICES, validators=[DataRequired()])
    preferred_fulfillment_date = DateField("Preferred Fulfillment Date", validators=[DataRequired()])
    patient_name = StringField("Patient Name (optional)", validators=[Optional(), Length(max=80)])
    notes = TextAreaField("Notes (optional)", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Send Exchange Request")

    def validate_preferred_fulfillment_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("Preferred fulfillment date cannot be in the past.")


class ExchangeActionForm(FlaskForm):
    submit = SubmitField("Confirm")
