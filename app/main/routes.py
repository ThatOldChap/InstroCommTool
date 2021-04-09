from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from app import db
from app.main.forms import ChannelForm, TestPointForm, EmptyForm, AddChannelForm, NewChannelForm, TestSubmitForm
from app.models import Channel, TestPoint
from app.main import bp
from app.main.measurements import ENG_UNITS

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    
    # Setup the button to add a new Channel
    testForm = TestSubmitForm()
    if testForm.validate_on_submit():
        return redirect(url_for('main.test')) 

    return render_template('index.html', title='Home', form=testForm)

@bp.route('/channel_view', methods=['GET', 'POST'])
def channel_view():

    # Setup the button to add a new Channel
    addChannelForm = EmptyForm('Add New Channel')    
    if addChannelForm.validate_on_submit():
        return redirect(url_for('main.add_channel'))        

    # class ChannelView

    # Create the lists for populating the fixed fields for each channel
    testPointLists = []

    # Create a form and get a list of all channels in the database    
    channelForm = ChannelForm()
    channelList = Channel.query.all()

    for channel in channelList:

        # Get the list of TestPoints for the channel
        testPointList = TestPoint.query.filter_by(channel_id=channel.id).all()
        testPointLists.append(testPointList)

        # Create a TestPointForm for the number of testpoints with that channel id
        for testPoint in testPointList:
            
            # Create a TestPointForm
            testPointForm = TestPointForm()

            # Assign the values to the editable fields
            testPointForm.measured_val = testPoint.measured_val
            testPointForm.date_performed = testPoint.date_performed
            testPointForm.notes = testPoint.notes

            # Add the TestPointForm to the ChannelForm
            channelForm.testPoints.append_entry(testPointForm)
            
    return render_template('channel_view.html', channelForm=channelForm, addChannelForm=addChannelForm,
                            testPointLists=testPointLists, channelList=channelList)
        
@bp.route('/add_channel', methods=['GET', 'POST'])
def add_channel():

    # Create the form for the new channel
    form = AddChannelForm()

    if form.validate_on_submit():

        # Check fields and add to the database
        channel = Channel(
            name=form.name.data,
            _type=form.ch_type.data, 
            range_min=form.range_min.data,
            range_max=form.range_max.data,
            nominal_eu=form.nominal_eu.data,
            full_scale_range=form.full_scale_range.data,
            full_scale_eu=form.full_scale_eu.data,
            tolerance=form.tolerance.data,
            tolerance_type=form.tolerance_type.data,
            test_range_min=form.test_range_min.data,
            test_range_max=form.test_range_max.data,
            input_eu=form.input_eu.data
        )
        db.session.add(channel)
        db.session.commit()
        flash('Channel {} has been added to the database'.format(channel.name))

        # Generate the default test points for the new channel
        channel.generate_default_test_points(5)
        db.session.commit()

        return redirect(url_for('main.channel_view'))
    
    return render_template('add_channel_form.html', title='Add Channel', addChannelForm=form)

@bp.route('/test', methods=['GET', 'POST'])
def test():

    newChannelForm = NewChannelForm()

    if newChannelForm.validate_on_submit():

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
            input_eu=newChannelForm.input_eu.data,
            
        )

        #Take the data from the form and commit to the db
        print(f'name = {newChannelForm.name.data}')
        print(f'meas_type = {newChannelForm.meas_type.data}')
        print(f'meas_eu = {newChannelForm.meas_eu.data}')
        print(f'meas_range_min = {newChannelForm.meas_range_min.data}')
        print(f'meas_range_max = {newChannelForm.meas_range_max.data}')
        print(f'full_scale = {newChannelForm.full_scale.data}')
        print(f'tolerance = {newChannelForm.tolerance.data}')
        print(f'tolerance_type = {newChannelForm.tolerance_type.data}')
        print(f'input_range_min = {newChannelForm.input_range_min.data}')
        print(f'input_range_max = {newChannelForm.input_range_max.data}')
        print(f'input_eu = {newChannelForm.input_eu.data}')
        print(f'num_test_points = {newChannelForm.num_test_points.data}')
        print(f'test_point_type = {newChannelForm.test_point_type.data}')

        # Look at naming input fields like input_val_eu[1] and accessing them as [x:-1] to get contents

        for tpNum, value in enumerate(newChannelForm.test_point_list.data):
            print(f'tp{tpNum} input_val = {value["input_val"]}')
            print(f'tp{tpNum} nominal_val = {value["nominal_val"]}')

        return redirect(url_for('main.index'))    

    return render_template('new_channel.html', title='Add New Channel', form=newChannelForm, units_dict=ENG_UNITS)
