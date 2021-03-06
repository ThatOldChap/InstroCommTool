from datetime import datetime
import dateutil.parser as dt
from flask import render_template, flash, redirect, url_for, request, current_app, g, jsonify
from flask_login import current_user, login_required
from app import db
from app.main.forms import ChannelForm, TestPointForm, NewChannelForm, ChannelListForm
from app.main.forms import CustomerForm, ProjectForm, JobForm, ChannelGroupForm, NewTestEquipmentForm
from app.models import Channel, TestPoint, Project, Customer, Job, ChannelGroup, TestEquipment, TestEquipmentType
from app.main import bp
from app.main.measurements import ENG_UNITS
from wtforms import BooleanField

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    
    summary = {}
    summary['customers'] = Customer.query.count()
    summary['projects'] = Project.query.count()
    summary['jobs'] = Job.query.count()
    summary['groups'] = ChannelGroup.query.count()
    summary['channels'] = Channel.query.count()
    summary['test equipment'] = TestEquipment.query.count()
    summary['test equipment types'] = TestEquipmentType.query.count()

    return render_template('index.html', title='Home', summary=summary)


@bp.route('/job_list', methods=['GET', 'POST'])
def job_list():

    job_list = Job.query.all()

    return render_template('job_list.html', title='Job List', job_list=job_list)


@bp.route('/group_list', methods=['GET', 'POST'])
def group_list():

    group_list = ChannelGroup.query.all()

    return render_template('group_list.html', title='Group List', group_list=group_list)


@bp.route('/new_customer', methods=['GET', 'POST'])
def new_customer():

    form = CustomerForm()

    if form.validate_on_submit():
        customer = Customer(name=form.name.data)
        db.session.add(customer)
        db.session.commit()
        flash(f'Customer {customer.name} has been added to the database.')
        return redirect(url_for('main.index'))

    return render_template('new_customer.html', title='New Customer', form=form)

@bp.route('/new_project', methods=['GET', 'POST'])
def new_project():

    form = ProjectForm()
    form.customer.choices = [("", "Select Customer")] + [(c.id, c.name) for c in Customer.query.order_by('name')]

    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            number=form.number.data,
            customer_id=form.customer.data
            )
        db.session.add(project)
        db.session.commit()
        flash(f'Project {project.name} has been added to the database.')
        return redirect(url_for('main.index'))

    return render_template('new_project.html', title='New Project', form=form)

@bp.route('/new_job', methods=['GET', 'POST'])
def new_job():

    form = JobForm()
    form.customer_name.choices = [("", "Select Name")] + [(c.id, c.name) for c in Customer.query.order_by('name')]
    form.project_number.choices = [("", "Select Number")] + [(p.id, p.number) for p in Project.query.order_by('number')]
    form.project_name.choices = [("", "Select Name")] + [(p.id, p.name) for p in Project.query.order_by('name')]

    if form.validate_on_submit():
        job = Job(
            project_id=form.project_name.data,
            phase=form.phase.data,
            job_type=form.job_type.data
            )
        db.session.add(job)
        db.session.commit()
        flash(f'Job {job.project_name()} {job.phase} {job.job_type} has been added to the database.')
        return redirect(url_for('main.index'))

    return render_template('new_job.html', title='New Job', form=form)

@bp.route('/job/<job_id>/new_group', methods=['GET', 'POST'])
def new_group(job_id):

    form = ChannelGroupForm()
    form.job_id.data = job_id

    if form.validate_on_submit():

        group = ChannelGroup(name=form.name.data, job_id=form.job_id.data)
        db.session.add(group)
        db.session.commit()
        flash(f'Group {group.name} has been added to the database.')
        return redirect(url_for('main.index'))

    return render_template('new_group.html', title='New Group', form=form)


@bp.route('/group/<group_id>/new_channel', methods=['GET', 'POST'])
def new_channel(group_id):
    
    test_equipment_types = TestEquipmentType.query.all()
    for test_equipment_type in test_equipment_types:
        # Create field(s) for each query result
        setattr(NewChannelForm, f'checkbox_{test_equipment_type.name}', BooleanField(label=test_equipment_type.name, id=f'checkbox-{test_equipment_type.id}'))

    newChannelForm = NewChannelForm()
    newChannelForm.group_id.data = group_id

    if newChannelForm.validate_on_submit():
        print('Form has been validated')
        
        # Collect variables being used multiple times
        style = newChannelForm.test_point_type.data
        test_point_list = newChannelForm.test_point_list.data
        meas_vals = []
        input_vals = []
        
        # Create the channel and commit to the db to get an id
        channel = Channel(
            name=newChannelForm.name.data,
            group_id=newChannelForm.group_id.data,
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
        if style == "Custom":
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

        for test_equipment_type in test_equipment_types:
            if newChannelForm.data[f'checkbox_{test_equipment_type.name}']:
                channel.add_test_equipment_type(test_equipment_type)

        print(f'Channel {channel.name} now has the following required test equipment:\n {channel.required_test_equipment()}')

        db.session.commit()
        flash(f'Channel {channel.name} has been added to the database.')     

        return redirect(url_for('main.index'))    

    print(newChannelForm.errors.items())

    return render_template('new_channel.html', title='Add New Channel', form=newChannelForm, units_dict=ENG_UNITS,
                            test_equipment_types=test_equipment_types)

@bp.route('/channel_list', methods=['GET', 'POST'])
def channel_list():

    # Get a list of the channels in the database
    channel_list = Channel.query.all()

    # Initialize the master channel_group_form that is passed to the template
    channel_list_form = ChannelListForm()

    for channel in channel_list:

        # Get a list of all the testpoints in each channel
        testpoint_list = channel.all_test_points()  
        test_equipment_types = channel.required_test_equipment()

        for test_equipment_type in test_equipment_types:
            # Create field(s) for each query result
            setattr(ChannelForm, f'equip_{test_equipment_type.id}', BooleanField(label=test_equipment_type.name, id=f'equip-{test_equipment_type.id}'))

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
 

@bp.route('/update_channel', methods=['POST'])
def update_channel():

    # Find the testpoint being updated from the database
    ch_id = request.form['chId']
    channel = Channel.query.filter_by(id=ch_id).first()

    # Check and write the new values to the database
    if 'signed_owner' in request.form:
        channel.signed_owner = request.form['signed_owner']

    # Check and write the new values to the database
    if 'signed_customer' in request.form:
        channel.signed_customer = request.form['signed_customer']

    if 'date' in request.form:
        js_date = request.form['date']
        new_date = dt.parse(js_date)
        channel.last_updated = new_date

    # Save the changes to the database
    db.session.commit()

    return jsonify({'message': f'Channel [{channel.name}] has been updated'})


@bp.route('/update_testpoint', methods=['POST'])
def update_testpoint():

    # Find the testpoint and channel being updated from the database
    tp_id = request.form['tpId']
    ch_id = request.form['chId']
    testpoint = TestPoint.query.filter_by(id=tp_id).first()
    channel = Channel.query.filter_by(id=ch_id).first()

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

    if 'notes' in request.form:
        testpoint.notes = request.form['notes']
    
    if 'pf' in request.form:
        testpoint.pf = request.form['pf']

    if 'date' in request.form:
        js_date = request.form['date']
        new_date = dt.parse(js_date)
        testpoint.date = new_date
        channel.last_updated = new_date

    # Save the changes to the database
    db.session.commit()

    return jsonify({'message': f'TestPoint [{testpoint.id}] has been updated'})


@bp.route('/get_updated_progress', methods=['GET', 'POST'])
def get_updated_progress():

    # Find the channel queried from the database
    id = request.form['chId']
    channel = Channel.query.filter_by(id=id).first()
    progress = channel.progress()
    completion = channel.completion()

    return jsonify({'progress': progress, 'completion': completion})

@bp.route('/new_test_equipment', methods=['GET', 'POST'])
def new_test_equipment():

    form = NewTestEquipmentForm()

    if form.validate_on_submit():

        test_equipment = TestEquipment(
            owner_id=form.owner_id.data,
            name=form.name.data,
            manufacturer=form.manufacturer.data,
            model_num=form.model_num.data,
            serial_num=form.serial_num.data,
            cal_due_date=form.cal_due_date.data
        )        
        db.session.add(test_equipment)
        db.session.commit()
        flash(f'TestEquipment {test_equipment.owner_id} {test_equipment.name} has been added to the database.')

        return redirect(url_for('main.index'))

    return render_template('new_test_equipment.html', title='New Test Equipment', form=form)

@bp.route('/new_test_equipment_type', methods=['GET', 'POST'])
def new_test_equipment_type():

    form = NewTestEquipmentForm()

    if form.validate_on_submit():

        test_equipment_type = TestEquipmentType(name=form.name.data)        
        db.session.add(test_equipment_type)
        db.session.commit()
        flash(f'TestEquipmentType {test_equipment_type.name} has been added to the database.')

        return redirect(url_for('main.index'))

    return render_template('new_test_equipment_type.html', title='New Test Equipment Type', form=form)

@bp.route('/job/<job_id>', methods=['GET', 'POST'])
def job(job_id):

    job = Job.query.filter_by(id=job_id).first_or_404()
    group_list = job.all_groups()

    return render_template('group_list.html', title='Group List', group_list=group_list, job=job)

@bp.route('/group/<group_id>', methods=['GET', 'POST'])
def group_channels(group_id):

    group = ChannelGroup.query.filter_by(id=group_id).first_or_404()
    channel_list = group.all_channels()
    channel_list_form = ChannelListForm()

    for channel in channel_list:

        testpoint_list = channel.all_test_points()
        test_equipment_types = channel.required_test_equipment()

        for test_equipment_type in test_equipment_types:
            setattr(ChannelForm, f'equip_{test_equipment_type.id}', BooleanField(label=test_equipment_type.name, id=f'equip-{test_equipment_type.id}'))

        channel_form = ChannelForm()

        for testpoint in testpoint_list:

            testpoint_form = TestPointForm()
            channel_form.testpoints.append_entry(testpoint_form)
        
        channel_list_form.channels.append_entry(channel_form)

    return render_template('channel_list.html', title='Channel List', channel_list_form=channel_list_form,
                            units_dict=ENG_UNITS, channel_list=channel_list)
