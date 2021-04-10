from datetime import datetime, timedelta
from time import time
from flask import current_app
from app import db
import math

# List of all the engineering units (eu)
eu_lookup = ['degC', 'Ohms', 'Hz', 'V', 'mA']

class Channel(db.Model):
	# Basic channel info
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	meas_type = db.Column(db.Integer) # 0 = RTD, 1 = Pressure, 2 = Frequency, etc...

	# Measurement Range info
	meas_range_min = db.Column(db.Float(16))
	meas_range_max = db.Column(db.Float(16))
	meas_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	full_scale = db.Column(db.Float(16))

	# Channel Tolerance info
	tolerance = db.Column(db.Float(8))
	tolerance_type = db.Column(db.Integer) # 0 = Units, 1 = %FS, 2 = %RDG, 3 = Custom, etc...

	# Test Point Input Range Info
	input_range_min = db.Column(db.Float(16))
	input_range_max = db.Column(db.Float(16))
	input_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...

	# List of Test Points
	test_points = db.relationship('TestPoint', backref='channel', lazy='dynamic')

	# Future Fields:
	#cal_eq_id_1 = db.Column(db.Integer)
	#cal_eq_id_1_due_date = db.Column(db.DateTime, default=datetime.utcnow)
	
	def __repr__(self):
		return '<Channel {}>'.format(self.name)

	def create_test_point_list(self, num_test_points, style, input_val_list, nominal_val_list):

		# Debugging variables
		num_test_points_added = 0

		# Custom, User-chosen test points
		if style == 2:
			# Create the TestPoints from the provided info
			for i in range(num_test_points):
				test_point = TestPoint(
					channel_id=self.id,
					input_val=input_val_list[i],
					nominal_val=nominal_val_list[i]
				)
				self.test_points.append(test_point)
				num_test_points_added += 1	

		# Default, auto-generated test points
		else:		
			# Calculates the nominal values for the measurement points	
			meas_range = self.meas_range()
			div = meas_range / num_test_points
			nominal_vals = [self.meas_range_min]
			for i in range(1, num_test_points):
				nominal_vals.append(nominal_vals[i-1] + div)
			
			# Calculates the input values for the input points
			input_range = self.input_range()
			div = input_range / num_test_points
			input_vals = [self.input_range_min]
			for i in range(1, num_test_points):
				input_vals.append(input_vals[i-1] + div)		

			# Create the TestPoints and add to them to the database
			for i in range(num_test_points):
				test_point = TestPoint(
					channel_id=self.id,
					input_val=input_vals[i],
					nominal_val=nominal_vals[i]
				)
				self.test_points.append(test_point)
				num_test_points_added += 1
		
		print(f'{num_test_points_added} TestPoints added to channel {self.name}')

	def meas_range(self):
		return self.meas_range_max - self.meas_range_min

	def input_range(self):
		return self.input_range_max - self.input_range_min

	def all_test_points():
		return TestPoint.query.filter_by(channel_id=self.id).all()

	def decode_eu(self, input_eu):
		return eu_lookup[input_eu]

	def get_tolerance_type(self):
		if self.tolerance_type == 0:
			return eu_lookup[self.eu]
		elif self.tolerance_type == 1:
			return f'%FS'
		elif self.tolerance_type == 2:
			return '%RDG'
	

class TestPoint(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
	input_val = db.Column(db.Float(16))
	meas_val = db.Column(db.Float(16))
	nominal_val = db.Column(db.Float(16))
	pf = db.Column(db.Integer) # 0 = Untested, 1 = Pass, 2 = Fail
	date_performed = db.Column(db.DateTime, default=datetime.utcnow)
	notes = db.Column(db.String(128))
	
	def __repr__(self):
		return '<TestPoint {} for Channel id {}>'.format(self.id, self.channel_id)

	def get_channel(self):
		return Channel.query.filter_by(id=self.channel_id).first()

	def get_tolerance_type(self):
		return self.get_channel().tolerance_type

	def calc_error(self):
		return self.nominal_val - self.measured_val

	def calc_pf(self):
		if abs(self.calc_error()) > self.error_limit(self.get_tolerance_type()):
			self.pf = 0
			return 'Fail'
		else:
			self.pf == 1
			return 'Pass'
	
	def low_limit(self):
		return self.nominal_val - self.error_limit(self.get_tolerance_type())

	def high_limit(self):
		return self.nominal_val + self.error_limit(self.get_tolerance_type())

	# Need to handle EU or %
	def error_limit(self, get_tolerance_type):
		ch = self.get_channel()
		if get_tolerance_type == 0: # EU
			return ch.tolerance

		elif get_tolerance_type == 1: # %FS
			return ch.full_scale_range * (ch.tolerance / 100)	

		elif get_tolerance_type == 2: # %RDG
			return self.nominal_val * (ch.tolerance / 100) 
	
		# elif get_tolerance_type == 3: # Custom
			# TODO: Figure out how to handle a 1 %RDG + 0.05 %FS style error

		else: # Error condition
			return -999
	

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	number = db.Column(db.Integer)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))


class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	projects = db.relationship('Project', backref='customer', lazy='dynamic')
