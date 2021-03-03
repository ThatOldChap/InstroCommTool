from datetime import datetime, timedelta
from time import time
from flask import current_app
from app import db
import math

# List of all the engineering units (eu)
eu_lookup = ['degC', 'Ohms', 'Hz', 'V', 'mA']

class Channel(db.Model):	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	_type = db.Column(db.Integer) # 0 = RTD, 1 = Pressure, 2 = Frequency, etc...
	range_min = db.Column(db.Float(16))
	range_max = db.Column(db.Float(16))
	eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	full_scale_range = db.Column(db.Float(16))
	full_scale_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	tolerance = db.Column(db.Float(8))
	tolerance_type = db.Column(db.Integer) # 0 = EU, 1 = %FS, 2 = %RDG, 3 = Custom, etc...
	test_range_min = db.Column(db.Float(16))
	test_range_max = db.Column(db.Float(16))
	test_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	test_points = db.relationship('TestPoint', backref='channel', lazy='dynamic')
	cal_eq_id_1 = db.Column(db.Integer)
	cal_eq_id_1_due_date = db.Column(db.DateTime, default=datetime.utcnow)
	
	def __repr__(self):
		return '<Channel {}>'.format(self.name)

	def test_point_list():
		return TestPoint.query.filter_by(channel_id=self.id).all()

	def decode_eu(self, eu):
		return eu_lookup[eu]

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
	measured_val = db.Column(db.Float(16))
	nominal_val = db.Column(db.Float(16))
	pf = db.Column(db.Integer) # 0 = Fail, 1 = Pass
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
			self.pf = 0 # Fail
			return 'Fail'
		else:
			self.pf = 1 # Pass
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
	
