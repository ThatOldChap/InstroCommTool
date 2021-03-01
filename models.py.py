from datetime import datetime, timedelta
from time import time
from flask import current_app
from app import db


class Channel(db.Model):	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	type = db.Column(db.Integer) # 0 = RTD, 1 = Pressure, 2 = Frequency, etc...
	min_range = db.Column(db.Float(16))
	max_range = db.Column(db.Float(16))
	range_eu = db.Column(db.Integer) # 0 = degC, 1 = Hz, 2 = lbf, etc...
	tolerance = db.Column(db.Float(8))
	tolerance_eu = db.Column(db.Integer) # 0 = %FS, 1 = %RDG, 2 = EU, etc...
	test_points = db.relationship('TestPoint', backref='channel', lazy='dynamic')
	
	def __repr__(self):
		return '<Channel {}>'.format(self.name)
	
	
class TestPoint(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
	date_performed = db.Column(db.DateTime, default=datetime.utcnow)
	min = db.Column(db.Float(16))
	max = db.Column(db.Float(16))
	eu = db.Column(db.Integer) # 0 = ohms, 1 = Hz, 2 = mV/V, etc...
	error = db.Column(db.Float(12))
	error_eu = db.Column(db.Integer, db.ForeignKey('channel.range_eu'))
	pf = db.Column(db.Integer) # 0 = Fail, 1 = Pass
	notes = db.Column(db.String(128))
	cal_eq_id_1 = db.Column(db.Integer)
	cal_eq_id_1_due_date = db.Column(db.DateTime)
	cal_eq_id_2 = db.Column(db.Integer)
	cal_eq_id_2_due_date = db.Column(db.DateTime)
	
	def __repr__(self):
		return '<TestPoint {} for Channel id {}>'.format(self.id, self.channel_id)
	