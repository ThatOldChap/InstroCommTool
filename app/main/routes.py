from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from app import db
# from app.main.forms import 
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
    channels = Channel.query.all()

    return render_template('index.html', title='Home', channels=channels, testpoints=testpoints)

