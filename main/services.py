from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file, Blueprint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import common
from auth import User,get_login_pass_hash,set_login_pass_hash
from redis_db import redis_db

routes_services = Blueprint('services', __name__, template_folder='templates', static_folder='static')

def request_login():
	if request.form['password'] == get_login_pass_hash():
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

# Routes
routes_services.add_url_rule('/request_login', 'request_login', request_login, methods=['POST'])
routes_services.add_url_rule('/api/det_status', 'api_det_status', api_det_status, methods=['GET', 'POST'])
routes_services.add_url_rule('/api/lvw_status', 'api_lvw_status', api_lvw_status, methods=['GET', 'POST'])
routes_services.add_url_rule('/api/delete_detections', 'api_delete_detections', delete_detections, methods=['POST'])
routes_services.add_url_rule('/api/change_password', 'api_change_password', change_password, methods=['POST'])
