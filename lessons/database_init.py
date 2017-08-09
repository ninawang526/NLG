from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import ARRAY,JSON
import json
# Initialize Flask
app = Flask(__name__)
# Configure Flask application for SQL Alchemy
app.config.from_object('config')
# PostgreSQL database session initialization using
db = SQLAlchemy(app)

class Users(db.Model):
	uid = db.Column(db.String(28), primary_key = True, unique = True, index = True)
	name = db.Column(db.String, index = True)
	created_at = db.Column(db.Date, index = True)
	last_sign_in = db.Column(db.Date, index = True)
	email = db.Column(db.String, index = True)
	provider = db.Column(db.String)
	timezone = db.Column(db.String)
	gender = db.Column(db.String)
	age = db.Column(BIGINT)
	profession = db.Column(db.String)

class Sessions(db.Model):
	session_id = db.Column(db.String, primary_key = True, unique = True, index = True)
	title = db.Column(db.String)
	total_time = db.Column(Float())
	user_id = db.Column(db.String)
	session_date = db.Column(db.Date)
	api_version = db.Column(db.String)
	energy_recommendation = db.Column(db.String)
	energy_values = db.Column(JSON)
	vocal_variation = db.Column(db.Integer)
	error = db.Column(db.String)
	fillers_recommendation = db.Column(db.String)
	fillers_location = db.Column(ARRAY(Integer) )
	fillers_summary = db.Column(JSON)
	pauses = db.Column(db.JSON)
	start_times = db.Column(ARRAY(DECIMAL))
	end_times = db.Column(ARRAY(DECIMAL))
	wpm_average = db.Column(Float())
	wpm_recommendation = db.Column(db.String)
	wpm_variation = db.Column(JSON)
	transcript_array = db.Column(ARRAY(String))
	transcript_string = db.Column(db.String)
	prompt_id = db.Column(db.String)
