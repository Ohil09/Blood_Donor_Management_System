from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class AddStockForm(FlaskForm):
    """Form to add blood stock"""
    blood_group = SelectField(
        "Blood Group",
        choices=[
            ("O+", "O+"),
            ("O-", "O-"),
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ],
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
        choices=[
            ("O+", "O+"),
            ("O-", "O-"),
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ],
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


class SearchInventoryForm(FlaskForm):
    """Form to search donors by blood group and eligibility"""
    blood_group = SelectField(
        "Blood Group",
        choices=[
            ("", "-- All Blood Groups --"),
            ("O+", "O+"),
            ("O-", "O-"),
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ]
    )
    city = StringField("City (optional)")
    only_eligible = StringField("Only Eligible Donors", default="on")
    submit = SubmitField("Search")