from datetime import datetime, timedelta
from time import time
from flask import current_app
from app import db


class Channel(db.Model):	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	_type = db.Column(db.Integer) # 0 = RTD, 1 = Pressure, 2 = Frequency, etc...
	min_range = db.Column(db.Float(16))
	max_range = db.Column(db.Float(16))
	range_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	tolerance = db.Column(db.Float(8))
	tolerance_eu = db.Column(db.Integer) # 0 = %FS, 1 = %RDG, 2 = EU, etc...
	test_min_range = db.Column(db.Float(16))
	test_max_range = db.Column(db.Float(16))
	test_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	test_points = db.relationship('TestPoint', backref='channel', lazy='dynamic')
	cal_eq_id_1 = db.Column(db.Integer)
	cal_eq_id_1_due_date = db.Column(db.DateTime, default=datetime.utcnow)
	
	def __repr__(self):
		return '<Channel {}>'.format(self.name)

	def test_3p(self):
		# Return default points for a 3 point test based on mix/max

	def test_5p(self):
		# Return default points for a 5 point test based on min/max
	
	
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

	def tolerance(self):
		return Channel.query.filter_by(id=self.channel_id).first().tolerance

	# Need to handle EU or %
	def low_limit(self, tol_eu):
		if tol_eu == 'eu':
			limit = nominal_val - tolerance
		elif tol_eu == 'fs':
			limit = 
		return nominal_val - tolerance

	# Need to handle EU or %
	def high_limit(self):
		return nominal_val + tolerance
	
	def calc_error(self):

	def calc_pf(self):
