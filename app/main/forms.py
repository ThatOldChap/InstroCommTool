from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, \
    IntegerField, FloatField, FormField, FieldList
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Channel, TestPoint

TYPE_CHOICES = [(0, "RTD"),(1, "Pressure"),(2, "Frequency")]

class EmptyForm(FlaskForm):
    submit = SubmitField('Add a Channel')

class TestPointForm(FlaskForm):
    measured_val = FloatField('Measured')
    date_performed = StringField('Date Performed')    
    # date_performed = DateField('Date', format='%Y-%m-%d' ) 
    notes = StringField('Notes')

class ChannelForm(FlaskForm):
    testPoints = FieldList(FormField(TestPointForm))

class AddChannelForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    ch_type = SelectField('Type', choices=[(0, "RTD"),(1, "Pressure"),(2, "Frequency")], validators=[DataRequired()])
    range_min = FloatField('Minimum Range', validators=[DataRequired()])
    range_max = FloatField('Maximum Range', validators=[DataRequired()])
    eu = SelectField('EU', choices=[(0, "degC"),(1, "Ohms"),(2, "Hz")], validators=[DataRequired()])
    full_scale_range = FloatField('Full Scale Range', validators=[DataRequired()])
    full_scale_eu = SelectField('Full Scale EU', choices=[(0, "degC"),(1, "Ohms"),(2, "Hz")], validators=[DataRequired()])
    tolerance = FloatField('Tolerance', validators=[DataRequired()])
    tolerance_type = SelectField('Tolerance Type', choices=[(0, "EU"),(1, f"%FS"),(2, "%RDG")], validators=[DataRequired()])
    test_range_min = FloatField('Minimum Test Range', validators=[DataRequired()])
    test_range_max = FloatField('MaximumTest Range', validators=[DataRequired()])
    test_eu = SelectField('Test EU', choices=[(0, "degC"),(1, "Ohms"),(2, "Hz")], validators=[DataRequired()])
    submit = SubmitField('Add New Channel')