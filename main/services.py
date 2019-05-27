from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file, Blueprint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import json
import os

import common
from auth import User,get_login_pass_hash,set_login_pass_hash
from redis_db import redis_db

routes_services = Blueprint('services', __name__, template_folder='templates', static_folder='static')

def request_login():

	if request.form['password'] == get_login_pass_hash():
		if request.form['remember'] == "true":
			login_user(User(1),remember=True)
		else:
			login_user(User(1))
		return 'ok'
	else:
		return 'no'

@login_required
def api_det_status():
	if request.method == 'GET':
		det_status = int(redis_db.get_var('det_status'))
		return str(det_status)
	elif request.method == 'POST':
		if request.form['det'] == 'start':
			redis_db.publish('kinectalarm','det start')
		elif request.form['det'] == 'stop':
			redis_db.publish('kinectalarm','det stop')
		return 'ok'

@login_required
def api_lvw_status():
	if request.method == 'GET':
		lvw_status = int(redis_db.get_var('lvw_status'))
		return str(lvw_status)
	elif request.method == 'POST':
		if request.form['lvw'] == 'start':
			redis_db.publish('kinectalarm','lvw start')
		elif request.form['lvw'] == 'stop':
			redis_db.publish('kinectalarm','lvw stop')
		return 'ok'

@login_required
def api_change_tilt():
	tilt = request.form['tilt']
	redis_db.publish('kinectalarm','tilt {}'.format(tilt))
	return 'ok'

@login_required
def api_change_brightness():
	value = request.form['brightness']
	redis_db.publish('kinectalarm','brightness {}'.format(value))
	return 'ok'

@login_required
def api_change_contrast():
	value = request.form['contrast']
	redis_db.publish('kinectalarm','contrast {}'.format(value))
	return 'ok'

@login_required
def api_change_threshold():
	value = request.form['threshold']
	redis_db.publish('kinectalarm','threshold {}'.format(value))
	return 'ok'

@login_required
def api_change_sensitivity():
	value = request.form['sensitivity']
	redis_db.publish('kinectalarm','sensitivity {}'.format(value))
	return 'ok'

@login_required
def api_change_email_data():
	email_from = request.form['email_from']
	password = request.form['password']
	email_to = request.form['email_to']
	smtp_server_url = request.form['smtp_server_url']
	smtp_server_port = request.form['smtp_server_port']
	data = {
		"email_from": email_from,
		"password": password,
		"email_to": email_to,
		"smtp_server_url": smtp_server_url,
		"smtp_server_port": smtp_server_port}

	redis_db.publish('email_change_data','{}'.format(json.dumps(data)))
	return 'ok'

@login_required
def api_send_email_activate():
	activate = request.form['activate']
	redis_db.publish('email_activate',activate)
	return 'ok'

@login_required
def api_send_email_test():
	if request.form['email_test'] == 'true':
		redis_db.publish('email_send_test','')
	return 'ok'

@login_required
def change_password():
	set_login_pass_hash(request.form['password'])
	with open('/etc/gunicorn/password', 'w') as file:
		file.write(get_login_pass_hash())
	logout_user()
	return 'ok'

@login_required
def delete_detections():
	if request.form['delete_detections'] == 'true':
		redis_db.publish('kinectalarm','det rst')
	return 'ok'

@login_required
def delete_detection():
	value = request.form['delete_detection']
	redis_db.publish('kinectalarm','det del {}'.format(value))
	return 'ok'

@login_required
def system_reboot():
	value = request.form['system_reboot']
	redis_db.publish('event_warning','System Rebooting')
	os.system("reboot")
	return 'ok'

@login_required
def config_ssh():
	if request.form['ssh'] == 'false':
		redis_db.publish('event_info','SSH server shutdown')
		redis_db.set_var('ssh_activate','0')
		os.system("/etc/init.d/sshd stop")
		
	elif request.form['ssh'] == 'true':
		redis_db.publish('event_info','SSH server started')
		redis_db.set_var('ssh_activate','1')
		os.system("/etc/init.d/sshd start")
	return 'ok'

# Routes
routes_services.add_url_rule('/request_login', 'request_login', request_login, methods=['POST'])
routes_services.add_url_rule('/api/det_status', 'api_det_status', api_det_status, methods=['GET', 'POST'])
routes_services.add_url_rule('/api/lvw_status', 'api_lvw_status', api_lvw_status, methods=['GET', 'POST'])
routes_services.add_url_rule('/api/change_tilt', 'api_change_tilt', api_change_tilt, methods=['POST'])
routes_services.add_url_rule('/api/change_brightness', 'api_change_brightness', api_change_brightness, methods=['POST'])
routes_services.add_url_rule('/api/change_contrast', 'api_change_contrast', api_change_contrast, methods=['POST'])
routes_services.add_url_rule('/api/change_threshold', 'api_change_threshold', api_change_threshold, methods=['POST'])
routes_services.add_url_rule('/api/change_sensitivity', 'api_change_sensitivity', api_change_sensitivity, methods=['POST'])
routes_services.add_url_rule('/api/delete_detections', 'api_delete_detections', delete_detections, methods=['POST'])
routes_services.add_url_rule('/api/delete_detection', 'api_delete_detection', delete_detection, methods=['POST'])
routes_services.add_url_rule('/api/change_email_data', 'api_change_email_data', api_change_email_data, methods=['POST'])
routes_services.add_url_rule('/api/send_email_test', 'api_send_email_test', api_send_email_test, methods=['POST'])
routes_services.add_url_rule('/api/send_email_activate', 'api_send_email_activate', api_send_email_activate, methods=['POST'])
routes_services.add_url_rule('/api/change_password', 'api_change_password', change_password, methods=['POST'])
routes_services.add_url_rule('/api/system_reboot', 'system_reboot', system_reboot, methods=['POST'])
routes_services.add_url_rule('/api/config_ssh', 'config_ssh', config_ssh, methods=['POST'])
