from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, \
    IntegerField, FloatField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Channel, TestPoint

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class TestPointForm(FlaskForm):
    measured_val = FloatField('Measured')
    date_performed = StringField('Date Performed')
    notes = StringField('Notes')

class ChannelForm(FlaskForm):
    testPoints = FieldList(FormField(TestPointForm))
