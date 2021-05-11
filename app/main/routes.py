from datetime import datetime
import dateutil.parser as dt
from flask import render_template, flash, redirect, url_for, request, current_app, g, jsonify
from flask_login import current_user, login_required
from app import db
from app.main.forms import ChannelForm, TestPointForm, AddChannelForm, NewChannelForm, ChannelListForm
from app.models import Channel, TestPoint
from app.main import bp
from app.main.measurements import ENG_UNITS

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    
 

    return render_template('index.html', title='Home')
    

@bp.route('/job_list', methods=['GET', 'POST'])
def job_list():


    return render_template('job_list.html', title='Job List')


@bp.route('/group_list', methods=['GET', 'POST'])
def group_list():


    return render_template('group_list.html', title='Group List')


@bp.route('/new_channel', methods=['GET', 'POST'])
def new_channel():

    newChannelForm = NewChannelForm()

    if newChannelForm.validate_on_submit():

        # Collect variables being used multiple times
        style = newChannelForm.test_point_type.data
        test_point_list = newChannelForm.test_point_list.data
        meas_vals = []
        input_vals = []
        
        # Create the channel and commit to the db to get an id
        channel = Channel(
            name=newChannelForm.name.data,
            meas_type=newChannelForm.meas_type.data,
            meas_range_min=newChannelForm.meas_range_min.data,
            meas_range_max=newChannelForm.meas_range_max.data,
            meas_eu=newChannelForm.meas_eu.data,
            full_scale=newChannelForm.full_scale.data,
            tolerance=newChannelForm.tolerance.data,
            tolerance_type=newChannelForm.tolerance_type.data,
            input_range_min=newChannelForm.input_range_min.data,
            input_range_max=newChannelForm.input_range_max.data,
            input_eu=newChannelForm.input_eu.data
        )
        db.session.add(channel)
        db.session.commit()        

        # Collects the custom test point data only if selected 
        if style == 2:
            for tpNum, val in enumerate(test_point_list):
                meas_vals.append(val["meas_val"])
                input_vals.append(val["input_val"])

        # Creates and adds the TestPoints to the channel and database
        channel.create_test_point_list(
            num_test_points=int(newChannelForm.num_test_points.data),
            style=style,
            input_val_list=input_vals,
            meas_val_list=meas_vals
        )
        db.session.commit()
        flash(f'Channel {channel.name} has been added to the database.')

        return redirect(url_for('main.index'))    

        print(newChannelForm.errors.items())

    return render_template('new_channel.html', title='Add New Channel', form=newChannelForm, units_dict=ENG_UNITS)

@bp.route('/channel_list', methods=['GET', 'POST'])
def channel_list():

    # Get a list of the channels in the database
    channel_list = Channel.query.all()

    # Initialize the master channel_group_form that is passed to the template
    channel_list_form = ChannelListForm()

    for channel in channel_list:

        # Get a list of all the testpoints in each channel
        testpoint_list = channel.all_test_points()  

        # Initialize each channel_form
        channel_form = ChannelForm()              

        for testpoint in testpoint_list:
            
            # Initialize each testpoint_form
            testpoint_form = TestPointForm()

            # Add the testpoint_form to 
            channel_form.testpoints.append_entry(testpoint_form)

        # Add each channel_form to the master form
        channel_list_form.channels.append_entry(channel_form)

    return render_template('channel_list.html', title='Channel List', channel_list_form=channel_list_form, units_dict=ENG_UNITS, 
                            channel_list=channel_list)
 

@bp.route('/update_testpoint', methods=['POST'])
def update_testpoint():

    # Find the testpoint being updated from the database
    id = request.form['id']
    testpoint = TestPoint.query.filter_by(id=id).first()

    # Check and write the new values to the database
    if 'input_val' in request.form:
        new_input_val = request.form['input_val']
        if new_input_val == "":
            testpoint.input_val = None
        else:
            testpoint.input_val = new_input_val

    if 'meas_val' in request.form:
        new_meas_val = request.form['meas_val']
        if new_meas_val == "":
            testpoint.meas_val = None
        else:
            testpoint.meas_val = new_meas_val
    
    if 'error' in request.form:
        new_error = request.form['error']
        if new_error == "":
            testpoint.error = None
        else:
            testpoint.error = new_error 

    if 'date' in request.form:
        js_date = request.form['date']
        new_date = dt.parse(js_date)
        if new_date == "":
            testpoint.date = None
        else:
            testpoint.date = new_date

    if 'notes' in request.form:
        testpoint.notes = request.form['notes']
    
    if 'pf' in request.form:
        testpoint.pf = request.form['pf']

    # Save the changes to the database
    db.session.commit()

    return jsonify({'message': 'TestPoint has been updated'})