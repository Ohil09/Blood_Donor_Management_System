from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class ConfirmDonationForm(FlaskForm):
    donor_id = StringField("Donor ID", validators=[DataRequired(), Length(min=5, max=40)])
    donation_type = SelectField(
        "Donation Type",
        choices=[("whole_blood", "Whole Blood"), ("platelets", "Platelets"), ("plasma", "Plasma")],
        validators=[DataRequired()]
    )
    units = IntegerField("Units", validators=[DataRequired(), NumberRange(min=1, max=10)], default=1)
    note = TextAreaField("Notes (optional)", validators=[Optional(), Length(max=300)])
    submit = SubmitField("Confirm Donation")


class DonationRequestForm(FlaskForm):
    """Form for donors to request to donate blood at a specific hospital"""
    hospital_id = SelectField(
        "Select Hospital",
        validators=[DataRequired()]
    )
    units_offered = IntegerField(
        "Units Offered",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        default=1
    )
    urgency_level = SelectField(
        "Urgency Level",
        choices=[("low", "Low"), ("normal", "Normal"), ("high", "High")],
        validators=[DataRequired()],
        default="normal"
    )
    preferred_date = StringField(
        "Preferred Donation Date (YYYY-MM-DD)",
        validators=[Optional(), Length(max=10)]
    )
    additional_notes = TextAreaField(
        "Additional Notes",
        validators=[Optional(), Length(max=500)]
    )
    submit = SubmitField("Submit Donation Request")


class DonationRequestActionForm(FlaskForm):
    """Form for hospital admins to accept/reject donation requests"""
    action = SelectField(
        "Action",
        choices=[("accept", "Accept Request"), ("reject", "Reject Request")],
        validators=[DataRequired()]
    )
    rejection_reason = TextAreaField(
        "Rejection Reason (if rejecting)",
        validators=[Optional(), Length(max=300)]
    )
    submit = SubmitField("Submit Action")