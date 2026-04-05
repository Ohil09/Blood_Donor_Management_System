from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from app.constants import BLOOD_GROUP_CHOICES


class AddStockForm(FlaskForm):
    """Form to add blood stock"""
    blood_group = SelectField(
        "Blood Group",
        choices=BLOOD_GROUP_CHOICES,
        validators=[DataRequired()]
    )
    quantity = IntegerField(
        "Quantity (units)",
        validators=[
            DataRequired(),
            NumberRange(min=1, message="Quantity must be at least 1")
        ]
    )
    submit = SubmitField("Add Stock")


class DepleteStockForm(FlaskForm):
    """Form to deplete blood stock (after donation/request fulfilled)"""
    blood_group = SelectField(
        "Blood Group",
        choices=BLOOD_GROUP_CHOICES,
        validators=[DataRequired()]
    )
    quantity = IntegerField(
        "Quantity (units)",
        validators=[
            DataRequired(),
            NumberRange(min=1, message="Quantity must be at least 1")
        ]
    )
    submit = SubmitField("Deplete Stock")


class SearchDonorForm(FlaskForm):
    """Form to search donors by blood group, city, and eligibility"""
    blood_group = SelectField(
        "Blood Group",
        choices=[("", "-- All Blood Groups --")] + BLOOD_GROUP_CHOICES
    )
    city = StringField("City (optional)")
    only_eligible = BooleanField("Only Eligible Donors", default=True)
    submit = SubmitField("Search")