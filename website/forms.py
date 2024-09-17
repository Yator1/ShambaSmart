# trials with forms
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SelectField, FileField
from wtforms.validators import DataRequired

class AddCropForm(FlaskForm):
    name = StringField('Crop Name', validators=[DataRequired()])
    variety = StringField('Variety', validators=[DataRequired()])
    date_planted = DateField('Date Planted', validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    stage_name = SelectField('Stage', choices=[('planting', 'Planting'), ('transplanting', 'Transplanting')])
    date_recorded = DateField('Stage Date', validators=[DataRequired()])
    image = FileField('Plant Image')
