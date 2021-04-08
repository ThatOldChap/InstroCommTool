from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, \
    IntegerField, FloatField, FormField, FieldList
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms.widgets import HiddenInput
from app.models import Channel, TestPoint
from app.main.measurements import ENG_UNITS

class EmptyForm(FlaskForm):
    submit = SubmitField('Add Channel')

class TestSubmitForm(FlaskForm):
    submit = SubmitField('Test')

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

CHOICES_MEAS_TYPE = [("", "Select Type..."),(0, "RTD"),(1, "Pressure"),(2, "Frequency"),(3, "Voltage")]
# CHOICES_EU = [("", "Select Units..."),(0, "degC"),(1, "Ohms"),(2, "Hz"),(3, "V")]
CHOICES_EU = list(ENG_UNITS.items())
CHOICES_EU.insert(0, ("", 'Select Units...'))

CHOICES_TOLERANCE_TYPE = [("", "Select Type..."),(1, "Units"),(2, f"%FS"),(3, '%RDG')]
CHOICES_NUM_TEST_POINTS = [("", "Select Number..."),(1, "1"),(2, "2"),(3, "3"),(4, "4"),(5, "5"),(6, "6"),(7, "7"),(8, "8"),(9, "9"),(10, "10")]
CHOICES_TEST_POINT_TYPE = [(1, "Default"),(2, "Custom")]

class TestPointValuesForm(FlaskForm):

    # CSS attribute definitions
    kw_vals = {'class': 'form-control'}

    # Value definitions
    input_val = FloatField('Input Value', validators=[DataRequired()], render_kw=kw_vals)
    #input_val_eu = StringField(widget=HiddenInput)
    nominal_val = FloatField('Nominal Value', validators=[DataRequired()], render_kw=kw_vals)
    #nominal_val_eu = StringField(widget=HiddenInput)

class NewChannelForm(FlaskForm):

    # CSS attribute definitions
    kw_name = {'class': 'form-control', 'placeholder': 'ex. ChannelName01'}
    kw_meas_type = {'class': 'custom-select', 'placeholder': 'ex. Temperature'}
    kw_select_field = {'class': 'custom-select'}
    kw_meas_range_min = {'class': 'form-control', 'placeholder': 'ex. -20'}
    kw_meas_range_max = {'class': 'form-control', 'placeholder': 'ex. 50'}
    kw_full_scale = {'class': 'form-control', 'placeholder': 'ex. 70'}
    kw_tolerance = {'class': 'form-control', 'placeholder': 'ex. 1.5'}
    kw_test_range_min = {'class': 'form-control', 'placeholder': 'ex. 80'}
    kw_test_range_max = {'class': 'form-control', 'placeholder': 'ex. 120'}
    kw_submit = {'class': 'btn btn-primary'}

    # Field definitions - Channel
    name = StringField('Name', validators=[DataRequired()], render_kw=kw_name)
    meas_type = SelectField('Type', choices=CHOICES_MEAS_TYPE, validators=[DataRequired()], render_kw=kw_select_field)
    nominal_eu = SelectField('Units', choices=CHOICES_EU, validators=[DataRequired()], render_kw=kw_select_field)

    meas_range_min = FloatField('Minimum Range', validators=[DataRequired()], render_kw=kw_meas_range_min)
    meas_range_max = FloatField('Maximum Range', validators=[DataRequired()], render_kw=kw_meas_range_max)
    full_scale = FloatField('Full Scale Range', validators=[DataRequired()], render_kw=kw_full_scale)

    tolerance = FloatField('Tolerance', validators=[DataRequired()], render_kw=kw_tolerance)
    tolerance_type = SelectField('Tolerance Type', choices=CHOICES_TOLERANCE_TYPE, validators=[DataRequired()], render_kw=kw_select_field)

    # Field definitions - TestPoints
    test_range_min = FloatField('Minimum Range', validators=[DataRequired()], render_kw=kw_meas_range_min)
    test_range_max = FloatField('Maximum Range', validators=[DataRequired()], render_kw=kw_meas_range_max)
    input_eu = SelectField('Units', choices=CHOICES_EU, validators=[DataRequired()], render_kw=kw_select_field)

    num_test_points = SelectField('# of Test Points', choices=CHOICES_NUM_TEST_POINTS, validators=[DataRequired()], render_kw=kw_select_field)
    test_point_type = SelectField('Test Point Values', choices=CHOICES_TEST_POINT_TYPE, validators=[DataRequired()], render_kw=kw_select_field)

    # Field definitions - TestPoint Values
    test_point_list = FieldList(FormField(TestPointValuesForm))

    # Form submission
    submit = SubmitField('Add New Channel', render_kw=kw_submit)