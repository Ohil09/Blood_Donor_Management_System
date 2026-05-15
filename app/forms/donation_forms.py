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