from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from app import db
from app.main.forms import ChannelForm, TestPointForm, EmptyForm, AddChannelForm, NewChannelForm, TestSubmitForm
from app.main.forms import ChannelGroupForm
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

        # Collect variables being used multiple times
        style = newChannelForm.test_point_type.data
        test_point_list = newChannelForm.test_point_list.data
        nominal_vals = []
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
                nominal_vals.append(val["nominal_val"])
                input_vals.append(val["input_val"])

        # Creates and adds the TestPoints to the channel and database
        channel.create_test_point_list(
            num_test_points=int(newChannelForm.num_test_points.data),
            style=style,
            input_val_list=input_vals,
            nominal_val_list=nominal_vals
        )
        db.session.commit()
        flash(f'Channel {channel.name} has been added to the database.')

        return redirect(url_for('main.index'))    

    return render_template('new_channel.html', title='Add New Channel', form=newChannelForm, units_dict=ENG_UNITS)

@bp.route('/channel_list', methods=['GET', 'POST'])
def channel_list():

    # Gets a list of the channels in the database
    channel_list = Channel.query.all()
    channel_group_form = ChannelGroupForm()

    # Create a list of all TestPointItems
    testpoint_item_list = []

    for channel in channel_list:

        # Get a list of the channel's TestPoints
        testpoint_list = channel.all_test_points()
        channel_form = ChannelForm()

        for testpoint in testpoint_list:
            
            # Create a new TestPointForm
            testpoint_form = TestPointForm()

            # Assign the values to the editable fields
            testpoint_form.meas_val = testpoint.meas_val
            testpoint_form.input_val = testpoint.input_val
            testpoint_form.notes = testpoint.notes

            # Add the TestPointForm to the ChannelGroupForm
            channel_form.testpoints.append_entry(testpoint_form)

            # Assign the values to the fixed fields
            testpoint_item = TestPointItem(
                id=channel.id,
                name=channel.name,
                testpoint_form=testpoint_form,
                input_eu=channel.input_eu,
                low_limit=testpoint.low_limit(),
                high_limit=testpoint.high_limit(),
                meas_eu=channel.meas_eu,
                date=testpoint.date
            )
            testpoint_item_list.append(testpoint_item)
        
        # Add each channel to the channel group 
        channel_group_form.channels.append_entry(channel_form)

    return render_template('channel_list.html', title='Channel List', channel_group_form=channel_group_form, units_dict=ENG_UNITS, 
                            testpoint_item_list=testpoint_item_list, channel_form=channel_form)


class ChannelItem(object):
    channel_form = None
    testpoint_items = []

    # Constructor
    def __init__(self, channel_form, testpoint_items):
        self.channel_form = channel_form
        self.testpoint_items = testpoint_items
    
    def add_testpoint(testpoint_item):
        self.testpoint_items.append(testpoint_item)


class TestPointItem(object):
    id = 0
    name = ""
    testpoint_form = None
    input_eu = 0
    low_limit = 0
    high_limit = 0
    meas_eu = 0
    date = ""

    # Constructor
    def __init__(self, id, name, testpoint_form, input_eu, low_limit, high_limit,
                meas_eu, date):
        self.id = id
        self.name = name
        self.testpoint_form = testpoint_form
        self.low_limit = low_limit
        self.high_limit = high_limit
        self.meas_eu = meas_eu
        self.date = date    

@bp.route('/save_testpoint', methods=['GET', 'POST'])
def save_testpoint():
    print('Saving testpoint...')

    return redirect(url_for('main.index')) 