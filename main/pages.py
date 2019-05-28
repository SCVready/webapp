from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file, Blueprint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import common
import psutil
import shutil
import os

from auth import set_login_pass_hash,get_login_pass_hash
from redis_db import redis_db
from sqlite_db import sqlite_db
routes_pages = Blueprint('pages', __name__, template_folder='templates', static_folder='static')


@login_required
def index():
	return redirect(url_for('pages.dashboard'))

@login_required
def dashboard():

	if redis_db.ttl('emailsender_watchdog') >= 0:
		emailsender_running = True
	else: 
		emailsender_running = False

	if redis_db.ttl('kinectalarm_watchdog') >= 0:
		kinectalarm_running = True
	else: 
		kinectalarm_running = False
	
	presenceos_version = redis_db.get_var('presenceos_version')
	kinectalarm_version = redis_db.get_var('kinectalarm_version')
	webapp_version = redis_db.get_var('webapp_version')
	emailsender_version = redis_db.get_var('emailsender_version')
	
	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))
	det_num    = int(sqlite_db.get_number_detections())
	cpu = psutil.cpu_percent()
	ram = psutil.virtual_memory()[2]
	
	stats = os.statvfs('/')
	total = stats.f_frsize * stats.f_blocks
        free = stats.f_frsize * stats.f_bavail
	used = total - free
	used_percentage = float(used)/float(total)*100
	return render_template('dashboard.html',emailsender_running=emailsender_running,kinectalarm_running=kinectalarm_running,
det_started=det_status,lvw_started=lvw_status,cpu=cpu,ram=ram,disk=used_percentage,new_intrusions=0,total_intrusions=det_num,
presenceos_version=presenceos_version,kinectalarm_version=kinectalarm_version,webapp_version=webapp_version,emailsender_version=emailsender_version)

@login_required
def detection():

	if redis_db.ttl('emailsender_watchdog') >= 0:
		emailsender_running = True
	else: 
		emailsender_running = False

	if redis_db.ttl('kinectalarm_watchdog') >= 0:
		kinectalarm_running = True
	else: 
		kinectalarm_running = False

	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))
	det_num    = int(sqlite_db.get_number_detections())
	detections = sqlite_db.get_detecions()

	return render_template('detection.html',emailsender_running=emailsender_running,kinectalarm_running=kinectalarm_running,det_started=det_status,lvw_started=lvw_status,det_num = det_num,detections=detections)

@login_required
def get_det_image(det_number,img_number):
	filename = '/var/detections/{}_capture_{}.jpeg'.format(det_number,img_number)
	return send_file(filename, mimetype='image/png', add_etags=False, cache_timeout=0)

@login_required
def get_det_video(det_number):
	filename = sqlite_db.get_detecion_vid(det_number)
	return send_file(filename, mimetype='video/mp4', add_etags=False, cache_timeout=0)

@login_required
def get_det_tar(det_number):
	filename = sqlite_db.get_detecion_img(det_number)
	return send_file(filename, mimetype='application/zip', add_etags=False, cache_timeout=0)

@login_required
def liveview():

	if redis_db.ttl('emailsender_watchdog') >= 0:
		emailsender_running = True
	else: 
		emailsender_running = False

	if redis_db.ttl('kinectalarm_watchdog') >= 0:
		kinectalarm_running = True
	else: 
		kinectalarm_running = False

	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))
	tilt = int(redis_db.get_var('tilt'))
	brightness = int(redis_db.get_var('brightness'))
	contrast = int(redis_db.get_var('contrast'))

	return render_template('liveview.html',emailsender_running=emailsender_running,kinectalarm_running=kinectalarm_running,det_started=det_status,lvw_started=lvw_status,tilt=tilt,brightness=brightness,contrast=contrast)

@login_required
def options():

	if redis_db.ttl('emailsender_watchdog') >= 0:
		emailsender_running = True
	else: 
		emailsender_running = False

	if redis_db.ttl('kinectalarm_watchdog') >= 0:
		kinectalarm_running = True
	else: 
		kinectalarm_running = False
	det_status  = int(redis_db.get_var('det_status'))
	lvw_status  = int(redis_db.get_var('lvw_status'))
	threshold   = int(redis_db.get_var('threshold'))
	sensitivity = int(redis_db.get_var('sensitivity'))

	email_from       = redis_db.get_var('email_from')
	password         = redis_db.get_var('password')
	email_to         = redis_db.get_var('email_to')
	smtp_server_url  = redis_db.get_var('smtp_server_url')
	smtp_server_port = int(redis_db.get_var('smtp_server_port'))
	smtp_server_port = smtp_server_port if smtp_server_port > 0 else ''
	send_email_activate = int(redis_db.get_var('send_email_activate'))

	ssh_activate = int(redis_db.get_var('ssh_activate'))

	return render_template('options.html',emailsender_running=emailsender_running,kinectalarm_running=kinectalarm_running, det_started=det_status, lvw_started=lvw_status, threshold=threshold, sensitivity=sensitivity, 
		email_from=email_from, password=password, email_to=email_to, smtp_server_url=smtp_server_url ,
		smtp_server_port=smtp_server_port, send_email_activate=send_email_activate,ssh_activate=ssh_activate)

@login_required
def log():

	if redis_db.ttl('emailsender_watchdog') >= 0:
		emailsender_running = True
	else: 
		emailsender_running = False

	if redis_db.ttl('kinectalarm_watchdog') >= 0:
		kinectalarm_running = True
	else: 
		kinectalarm_running = False

	det_status = int(redis_db.get_var('det_status'))
	lvw_status = int(redis_db.get_var('lvw_status'))
	log_text = tuple()
	with open('/var/log/messages', 'r') as fp:
		line = fp.readline()
		while line:
			line = fp.readline()
			log_text = log_text + (line.strip().decode('utf-8'),)

	return render_template('log.html',emailsender_running=emailsender_running,kinectalarm_running=kinectalarm_running,det_started=det_status,lvw_started=lvw_status,log_text=log_text)

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
routes_pages.add_url_rule('/detection_tar/<det_number>_capture.zip', 'get_det_tar', get_det_tar, methods=['GET'])
routes_pages.add_url_rule('/detection_vid/<det_number>', 'get_det_video', get_det_video, methods=['GET'])

