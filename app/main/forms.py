from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, \
    IntegerField, FloatField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Channel, TestPoint

class EmptyForm(FlaskForm):
    submit = SubmitField('Add a Channel')

class TestPointForm(FlaskForm):
    measured_val = FloatField('Measured')
    date_performed = StringField('Date Performed')
    notes = StringField('Notes')

class ChannelForm(FlaskForm):
    testPoints = FieldList(FormField(TestPointForm))

class NewChannelForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    _type = SelectField('Type', choices=[(0, "RTD"),(1, "Pressure"),(2, "Frequency")])
    range_min = FloatField('Minimum Range', validators=[DataRequired()])
    range_max = FloatField('Maximum Range', validators=[DataRequired()])
    eu = SelectField('Type', choices=[(0, "degC"),(1, "Ohms"),(2, "Hz")])
    full_scale_range = FloatField('Full Scale Range', validators=[DataRequired()])
    full_scale_eu = SelectField('Type', choices=[(0, "degC"),(1, "Ohms"),(2, "Hz")])
    tolerance = FloatField('Tolerance', validators=[DataRequired()])
    tolerance_type = SelectField('Tolerance Type', choices=[(0, "EU"),(1, f"%FS"),(2, "%RDG")])
    test_range_min = FloatField('Minimum Test Range', validators=[DataRequired()])
    test_range_max = FloatField('MaximumTest Range', validators=[DataRequired()])
    test_eu = SelectField('Type', choices=[(0, "degC"),(1, "Ohms"),(2, "Hz")])
    submit = SubmitField('Add New Channel')