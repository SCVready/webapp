from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file, Blueprint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import common
from auth import set_login_pass_hash,get_login_pass_hash
from redis_db import redis_db
from sqlite_db import sqlite_db
routes_pages = Blueprint('pages', __name__, template_folder='templates', static_folder='static')


@login_required
def index():
	return redirect(url_for('pages.dashboard'))

@login_required
def dashboard():
	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))

	return render_template('dashboard.html',det_started=det_status,lvw_started=lvw_status)

@login_required
def detection():
	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))
	det_num    = int(sqlite_db.get_number_detecions())
	detections = sqlite_db.get_detecions()

	return render_template('detection.html',det_started=det_status,lvw_started=lvw_status,det_num = det_num,detections=detections)

@login_required
def get_det_image(det_number,img_number):
	filename = sqlite_db.get_detecions_filename(det_number)
	return send_file(filename, mimetype='image/png', add_etags=False, cache_timeout=0)


@login_required
def liveview():
	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))

	return render_template('liveview.html',det_started=det_status,lvw_started=lvw_status)

@login_required
def options():
	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))
	
	return render_template('options.html',det_started=det_status,lvw_started=lvw_status)

@login_required
def log():
	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))

	return render_template('log.html',det_started=det_status,lvw_started=lvw_status)

def login():
	return render_template('login.html')

@login_required
def logout():
	logout_user()
	return redirect(url_for('pages.login'))

# Routes
routes_pages.add_url_rule('/login', 'login', login, methods=['GET'])
routes_pages.add_url_rule('/logout', 'logout', logout, methods=['GET'])

routes_pages.add_url_rule('/', 'index', index, methods=['GET'])
routes_pages.add_url_rule('/dashboard', 'dashboard', dashboard, methods=['GET'])
routes_pages.add_url_rule('/detection', 'detection', detection, methods=['GET', 'POST'])
routes_pages.add_url_rule('/liveview', 'liveview', liveview, methods=['GET', 'POST'])
routes_pages.add_url_rule('/options', 'options', options, methods=['GET'])
routes_pages.add_url_rule('/log', 'log', log, methods=['GET'])
routes_pages.add_url_rule('/detection/<det_number>/<img_number>', 'get_det_image', get_det_image, methods=['GET'])


