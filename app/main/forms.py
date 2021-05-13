from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, \
    IntegerField, FloatField, FormField, FieldList
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms.widgets import HiddenInput
from app.models import Channel, TestPoint
from app.main.measurements import ENG_UNITS
from enum import Enum

class EmptyForm(FlaskForm):
    submit = SubmitField('Add Channel')

class TestSubmitForm(FlaskForm):
    submit = SubmitField('Test')

class TestPointForm(FlaskForm):
    meas_val = FloatField('Measured', validators=[DataRequired()])
    input_val = FloatField('Input', validators=[DataRequired()])    
    notes = StringField('Notes')

class ChannelForm(FlaskForm):
    testpoints = FieldList(FormField(TestPointForm))

EMPTY_CHOICE = ("", 'Select Units...')

CHOICES_MEAS_TYPE = [("", "Select Type..."),("RTD", "RTD"),("Pressure", "Pressure"),("Frequency", "Frequency"),("Voltage", "Voltage")]

CHOICES_EU = list(ENG_UNITS.items())
CHOICES_EU.insert(0, EMPTY_CHOICE)

CHOICES_TOLERANCE_TYPE = [("", "Select Type..."),("EU", "EU"),(f"%FS", f"%FS"),('%RDG', '%RDG')]
CHOICES_NUM_TEST_POINTS = [("", "Select Number..."),(1, "1"),(2, "2"),(3, "3"),(4, "4"),(5, "5"),(6, "6"),(7, "7"),(8, "8"),(9, "9"),(10, "10")]
CHOICES_TEST_POINT_TYPE = [("Default", "Default"),("Custom", "Custom")]

class TestPointValuesForm(FlaskForm):

    # CSS attribute definitions
    kw_vals = {'class': 'form-control'}

    # Value definitions
    input_val = FloatField('Input Value', validators=[DataRequired()], render_kw=kw_vals)
    meas_val = FloatField('Nominal Value', validators=[DataRequired()], render_kw=kw_vals)

class NewChannelForm(FlaskForm):

    # CSS attribute definitions
    kw_name = {'class': 'form-control', 'placeholder': 'ex. ChannelName01'}
    kw_meas_type = {'class': 'custom-select', 'placeholder': 'ex. Temperature'}
    kw_select_field = {'class': 'custom-select'}
    kw_meas_range_min = {'class': 'form-control', 'placeholder': 'ex. -20'}
    kw_meas_range_max = {'class': 'form-control', 'placeholder': 'ex. 50'}
    kw_full_scale = {'class': 'form-control', 'placeholder': 'ex. 70'}
    kw_tolerance = {'class': 'form-control', 'placeholder': 'ex. 1.5'}
    kw_input_range_min = {'class': 'form-control', 'placeholder': 'ex. 80'}
    kw_input_range_max = {'class': 'form-control', 'placeholder': 'ex. 120'}
    kw_submit = {'class': 'btn btn-primary'}

    # TODO: Add custom validator to allow zero values
    # Basic Channel Info
    name = StringField('Name', validators=[DataRequired()], render_kw=kw_name)
    meas_type = SelectField('Type', choices=CHOICES_MEAS_TYPE, validators=[DataRequired()], render_kw=kw_select_field)

    # Measurement Range Info
    meas_range_min = FloatField('Minimum Range', validators=[DataRequired()], render_kw=kw_meas_range_min)
    meas_range_max = FloatField('Maximum Range', validators=[DataRequired()], render_kw=kw_meas_range_max)
    meas_eu = SelectField('Units', choices=CHOICES_EU, validators=[DataRequired()], render_kw=kw_select_field)
    full_scale = FloatField('Full Scale Range', validators=[DataRequired()], render_kw=kw_full_scale)

    # Channel Tolerance Info
    tolerance = FloatField('Tolerance', validators=[DataRequired()], render_kw=kw_tolerance)
    tolerance_type = SelectField('Tolerance Type', choices=CHOICES_TOLERANCE_TYPE, validators=[DataRequired()], render_kw=kw_select_field)

    # Test Point Input Range Info
    input_range_min = FloatField('Minimum Range', validators=[DataRequired()], render_kw=kw_meas_range_min)
    input_range_max = FloatField('Maximum Range', validators=[DataRequired()], render_kw=kw_meas_range_max)
    input_eu = SelectField('Units', choices=CHOICES_EU, validators=[DataRequired()], render_kw=kw_select_field)

    # Test Point Creation Info
    num_test_points = SelectField('# of Test Points', choices=CHOICES_NUM_TEST_POINTS, validators=[DataRequired()], render_kw=kw_select_field)
    test_point_type = SelectField('Test Point Values', choices=CHOICES_TEST_POINT_TYPE, validators=[DataRequired()], render_kw=kw_select_field)
    test_point_list = FieldList(FormField(TestPointValuesForm))

    # Form submission
    submit = SubmitField('Add New Channel', render_kw=kw_submit)

class ChannelListForm(FlaskForm):
    channels = FieldList(FormField(ChannelForm))

class ChannelGroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add New Group')

CHOICES_PHASE = [("", "Select Phase..."),("In-House", "In-House"),("On-Site", "On-Site")]
CHOICES_JOB_TYPE = [("", "Select Type..."),("Commissioning", "Commissioning"),("ATP", "ATP")]

class JobForm(FlaskForm):
    customer_name = SelectField('Customer Name', render_kw={'class': 'custom-select'}, validators=[DataRequired()])
    project_number = SelectField('Project Number', render_kw={'class': 'custom-select'}, validators=[DataRequired()])
    project_name = SelectField('Project Name', render_kw={'class': 'custom-select'}, validators=[DataRequired()])
    phase = SelectField('Project Phase', choices=CHOICES_PHASE, render_kw={'class': 'custom-select'}, validators=[DataRequired()])
    job_type = SelectField('Work Type', choices=CHOICES_JOB_TYPE, render_kw={'class': 'custom-select'}, validators=[DataRequired()])
    submit = SubmitField('Add New Job')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    number = IntegerField('Project Number', validators=[DataRequired()])
    customer = SelectField('Customer', render_kw={'class': 'custom-select'}, validators=[DataRequired()])
    submit = SubmitField('Add New Project')

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add New Customer')