from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from app import db
from app.main.forms import ChannelForm, TestPointForm
from app.models import Channel, TestPoint
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    
    c1 = Channel(
        name='ExhaustRTD01',
        eu=0,
        test_eu=1,
        tolerance=1.50,
        tolerance_type=0
    )
    channels = [c1]
    db.session.add(c1)
    db.session.commit()

    tp1 = TestPoint(
        channel_id=c1.id,
        input_val=150,
        nominal_val=200,
        measured_val=199.50,
        pf=1,
        date_performed=datetime(2021, 3, 2, 9, 31, 25),
        notes='Hope this works!'
    )
    tp2 = TestPoint(
        channel_id=c1.id,
        input_val=80,
        nominal_val=0,
        measured_val=1.75,
        pf=0,
        date_performed=datetime(2021, 3, 2, 9, 35, 57),
        notes='Darn thing'
    )
    tp3 = TestPoint(
        channel_id=c1.id,
        input_val=200,
        nominal_val=700,
        measured_val=702.50,
        pf=0,
        date_performed=datetime(2021, 3, 2, 10, 39, 11),
        notes='Welp, send help'
    )
    testpoints = [tp1, tp2, tp3]    
    db.session.add_all(testpoints)
    db.session.commit()
    #channels = Channel.query.all()

    return render_template('index.html', title='Home', channels=channels, testpoints=testpoints)

@bp.route('/channel_view', methods=['GET', 'POST'])
def channel_view():

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
            
    return render_template('channel_view.html', channelForm=channelForm,
                            testPointLists=testPointLists, channelList=channelList)
        

