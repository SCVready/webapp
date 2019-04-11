from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file, Blueprint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import common
from auth import set_login_pass_hash,get_login_pass_hash

routes_pages = Blueprint('pages', __name__, template_folder='templates', static_folder='static')


@login_required
def index():
	return redirect(url_for('pages.dashboard'))

@login_required
def dashboard():
	ret = common.send_command('req lvw status')
	if ret[0] == 1:
		return render_template('error.html')
	lvw_started_str = ret[1]
	if lvw_started_str == 'yes':
		lvw_started = True
	else:
		lvw_started = False
	print('lvw started %d' % (lvw_started))

	ret = common.send_command('req det status')
	if ret[0] == 1:
		return render_template('error.html')
	det_started_str = ret[1]
	if det_started_str == 'yes':
		det_started = True
	else:
		det_started = False
	print('det started %d' % (det_started))

	return render_template('dashboard.html',det_started=det_started,lvw_started=lvw_started)

@login_required
def detection():
	ret = common.send_command('req det status')
	if ret[0] == 1:
		return render_template('error.html')
	det_started_str = ret[1]
	if det_started_str == 'yes':
		det_started = True
	else:
		det_started = False
	print('det started %d' % (det_started))

	ret = common.send_command('req det num')
	if ret[0] == 1:
		return render_template('error.html')
	det_num = int(ret[1])

	ret = common.send_command('req lvw status')
	if ret[0] == 1:
		return render_template('error.html')
	lvw_started_str = ret[1]
	if lvw_started_str == 'yes':
		lvw_started = True
	else:
		lvw_started = False
	print('lvw started %d' % (lvw_started))

	return render_template('detection.html',det_started=det_started,lvw_started=lvw_started,det_num=det_num)

@login_required
def get_det_image(det_number,img_number):
	filename = '/var/detections/%s/capture_%s.jpeg' % (det_number,img_number)
	print(filename)
	return send_file(filename, mimetype='image/png', add_etags=False, cache_timeout=0)


@login_required
def liveview():
	ret = common.send_command('req lvw status')
	if ret[0] == 1:
		return render_template('error.html')
	lvw_started_str = ret[1]
	if lvw_started_str == 'yes':
		lvw_started = True
	else:
		lvw_started = False
	print('lvw started %d' % (lvw_started))

	ret = common.send_command('req det status')
	if ret[0] == 1:
		return render_template('error.html')
	det_started_str = ret[1]
	if det_started_str == 'yes':
		det_started = True
	else:
		det_started = False
	print('det started %d' % (det_started))

	return render_template('liveview.html',det_started=det_started,lvw_started=lvw_started)

@login_required
def options():
	ret = common.send_command('req lvw status')
	if ret[0] == 1:
		return render_template('error.html')
	lvw_started_str = ret[1]
	if lvw_started_str == 'yes':
		lvw_started = True
	else:
		lvw_started = False
	print('lvw started %d' % (lvw_started))

	ret = common.send_command('req det status')
	if ret[0] == 1:
		return render_template('error.html')
	det_started_str = ret[1]
	if det_started_str == 'yes':
		det_started = True
	else:
		det_started = False
	print('det started %d' % (det_started))	
	
	return render_template('options.html',det_started=det_started,lvw_started=lvw_started)

@login_required
def log():
	ret = common.send_command('req lvw status')
	if ret[0] == 1:
		return render_template('error.html')
	lvw_started_str = ret[1]
	if lvw_started_str == 'yes':
		lvw_started = True
	else:
		lvw_started = False
	print('lvw started %d' % (lvw_started))

	ret = common.send_command('req det status')
	if ret[0] == 1:
		return render_template('error.html')
	det_started_str = ret[1]
	if det_started_str == 'yes':
		det_started = True
	else:
		det_started = False
	print('det started %d' % (det_started))	
	return render_template('log.html',det_started=det_started,lvw_started=lvw_started)

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


