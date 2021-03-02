from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Channel, TestPoint

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class ChannelForm(FlaskForm):
    name = StringField('Name': validators=[DataRequired()])
    #_type = SelectField('Type')