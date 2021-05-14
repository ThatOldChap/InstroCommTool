from datetime import datetime, timedelta
from time import time
from flask import current_app
from app import db

import math

class Channel(db.Model):
	# Basic channel info
	id = db.Column(db.Integer, primary_key=True)
	group_id = db.Column(db.Integer, db.ForeignKey('channel_group.id'))
	name = db.Column(db.String(32))
	meas_type = db.Column(db.String(24)) # 0 = RTD, 1 = Pressure, 2 = Frequency, etc...

	# Measurement Range info
	meas_range_min = db.Column(db.Float(16))
	meas_range_max = db.Column(db.Float(16))
	meas_eu = db.Column(db.String(16)) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	full_scale = db.Column(db.Float(16))

	# Channel Tolerance info
	tolerance = db.Column(db.Float(8))
	tolerance_type = db.Column(db.String(8)) # 0 = Units, 1 = %FS, 2 = %RDG, 3 = Custom, etc...

	# Test Point Input Range Info
	input_range_min = db.Column(db.Float(16))
	input_range_max = db.Column(db.Float(16))
	input_eu = db.Column(db.String(16)) # 0 = degC, 1 = Hz, 2 = lbf, etc...

	# List of Test Points
	test_points = db.relationship('TestPoint', backref='channel', lazy='dynamic')

	# Future Fields:
	#cal_eq_id_1 = db.Column(db.Integer)
	#cal_eq_id_1_due_date = db.Column(db.DateTime, default=datetime.utcnow)
	
	def __repr__(self):
		return '<Channel {}>'.format(self.name)

	def create_test_point_list(self, num_test_points, style, input_val_list, meas_val_list):

		# Debugging variables
		num_test_points_added = 0

		# Custom, User-chosen test points
		if style == "Custom":
			# Create the TestPoints from the provided info
			for i in range(num_test_points):
				test_point = TestPoint(
					channel_id=self.id,
					input_val_nom=input_val_list[i],
					meas_val_nom=meas_val_list[i]
				)
				self.test_points.append(test_point)
				num_test_points_added += 1	

		# Default, auto-generated test points
		else:		
			# Calculates the nominal measured values for the measurement points	
			meas_range = self.meas_range()
			div = meas_range / (num_test_points - 1)
			meas_vals = [self.meas_range_min]
			for i in range(1, num_test_points):
				meas_vals.append(meas_vals[i-1] + div)
			
			# Calculates the nominal input values for the input points
			input_range = self.input_range()
			div = input_range / (num_test_points - 1) 
			input_vals = [self.input_range_min]
			for i in range(1, num_test_points):
				input_vals.append(input_vals[i-1] + div)		

			# Create the TestPoints and add to them to the database
			for i in range(num_test_points):
				test_point = TestPoint(
					channel_id=self.id,
					input_val_nom=input_vals[i],
					meas_val_nom=meas_vals[i]
				)
				self.test_points.append(test_point)
				num_test_points_added += 1
		
		print(f'{num_test_points_added} TestPoints added to channel {self.name}')

	def meas_range(self):
		return self.meas_range_max - self.meas_range_min

	def input_range(self):
		return self.input_range_max - self.input_range_min

	def all_test_points(self):
		return TestPoint.query.filter_by(channel_id=self.id).all()
	

class TestPoint(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
	input_val = db.Column(db.Float(16))
	input_val_nom = db.Column(db.Float(16))
	meas_val = db.Column(db.Float(16))
	meas_val_nom = db.Column(db.Float(16))
	error = db.Column(db.Float(8))
	pf = db.Column(db.String(8), default="Untested") # 0 = Untested, 1 = Pass, 2 = Fail, 3 = Post
	date = db.Column(db.DateTime)
	notes = db.Column(db.String(128))
	
	def __repr__(self):
		return '<TestPoint {} for Channel id {}>'.format(self.id, self.channel_id)

	def get_channel(self):
		return Channel.query.filter_by(id=self.channel_id).first()

	def calc_error(self):
		return self.meas_val_nom - self.measured_val

	def calc_tolerance(self):
		ch = self.get_channel()
		tolerance = ch.tolerance
		adj_tolerance = tolerance / 100
		tol_type = ch.tolerance_type
		
		if tol_type == 'EU':
			# EU
			return tolerance
		elif tol_type == f'%FS':
			# % FS
			return ch.full_scale * adj_tolerance
		elif tol_type == '%RDG':
			# % RDG
			return self.meas_val_nom * adj_tolerance
		# elif tol_type == 'Custom':
			# Custom
			
	def tol_type(self):
		return self.get_channel().tolerance_type
	
	def low_limit(self):
		return self.meas_val_nom - self.calc_tolerance()

	def high_limit(self):
		return self.meas_val_nom + self.calc_tolerance()


class ChannelGroup(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	last_updated = db.Column(db.DateTime, default=datetime.utcnow)
	channels = db.relationship('Channel', backref='channel_group', lazy='dynamic')
	job_id = db.Column(db.Integer, db.ForeignKey('job.id'))

	def all_channels(self):
		return Channel.query.filter_by(group_id=self.id).all()
	
	def num_channels(self):
		return Channel.query.filter_by(group_id=self.id).count()

	def num_testpoints(self):
		channels = self.all_channels()
		count = 0
		for ch in channels:
			count += len(ch.all_test_points())
		return count
	
	def completion(self):
		total = self.num_testpoints()
		status = self.status()
		num_passing = status['passed'] + status['post']
		if total == 0:
			return 'Not Started'
		elif num_passing < total:
			return 'In-Progress'
		elif num_passing == total:
			return 'Complete'

	def status(self):
		channels = self.all_channels()
		num_passed = 0
		num_post = 0
		num_failed = 0
		num_untested = 0

		for ch in channels:
			testpoints = ch.all_test_points()
			for tp in testpoints:
				pf = tp.pf
				if pf == 'Untested': num_untested += 1
				if pf == 'Pass': num_passed += 1
				if pf == 'Fail': num_failed += 1
				if pf == 'Post': num_post += 1

		return {'passed': num_passed, 'failed': num_failed, 'post': num_post, 'untested': num_untested}

	def progress(self):
		total = self.num_testpoints()
		if total > 0:
			status = self.status()
			passed = (status['passed'] / total) * 100
			post = (status['post'] / total) * 100
			failed = (status['failed'] / total) * 100
			untested = (status['untested'] / total) * 100
		else:
			passed = 0
			post = 0
			failed = 0
			untested = 100

		return {'passed': passed, 'failed': failed, 'post': post, 'untested': untested}


class Job(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	phase = db.Column(db.String(8))	# 0 = In-House, 1 = On-Site
	job_type = db.Column(db.String(16))	# 0 = Commissioning, 1 = ATP
	last_updated = db.Column(db.DateTime)
	channel_groups = db.relationship('ChannelGroup', backref='job', lazy='dynamic')

	def all_groups(self):
		return ChannelGroup.query.filter_by(job_id=self.id).all()

	def num_channels(self):
		groups = self.all_groups()
		count = 0
		for group in groups:
			count += group.num_channels()
		return count

	def get_project(self):
		return Project.query.filter_by(id=self.project_id).first()

	def get_customer(self):
		return self.get_project().get_customer()

	def customer_name(self):
		return self.get_customer().name

	def project_name(self):
		return self.get_project().name

	def project_number(self):
		return self.get_project().number

	def status(self):
		groups = self.all_groups()
		num_passed = 0
		num_post = 0
		num_failed = 0
		num_untested = 0

		for group in groups:
			pf = group.status()
			num_passed += pf['passed']
			num_post += pf['post']
			num_failed += pf['failed']
			num_untested += pf['untested']
		
		return {'passed': num_passed, 'failed': num_failed, 'post': num_post, 'untested': num_untested}

	def progress(self):
		total = self.num_channels()
		if total > 0:
			status = self.status()
			passed = (status['passed'] / total) * 100
			post = (status['post'] / total) * 100
			failed = (status['failed'] / total) * 100
			untested = (status['untested'] / total) * 100
		else:
			passed = 0
			post = 0
			failed = 0
			untested = 100

		return {'passed': passed, 'failed': failed, 'post': post, 'untested': untested}


class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	number = db.Column(db.Integer)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

	def all_jobs(self):
		return Job.query.filter_by(project_id=self.id).all()

	def get_customer(self):
		return Customer.query.filter_by(id=self.customer_id).first()


class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	projects = db.relationship('Project', backref='customer', lazy='dynamic')
