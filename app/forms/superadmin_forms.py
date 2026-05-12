from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class CreateHospitalForm(FlaskForm):
    name = StringField("Hospital Name", validators=[DataRequired(), Length(min=2, max=120)])
    city = StringField("City", validators=[DataRequired(), Length(min=2, max=80)])
    address = StringField("Address", validators=[Optional(), Length(max=200)])
    phone = StringField(
        "Contact Number",
        validators=[DataRequired(), Length(min=10, max=10, message="Phone number must be exactly 10 digits.")],
    )
    email = StringField("Hospital Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Generate Hospital ID & Password")
