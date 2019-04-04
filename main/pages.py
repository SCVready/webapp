from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file, Blueprint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import common
from auth import set_login_pass_hash,get_login_pass_hash

routes_pages = Blueprint('pages', __name__, template_folder='templates', static_folder='static')

@login_required
def index():
	if request.method == 'GET':
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
		return render_template('main.html',det_started=det_started,det_num=det_num)
	elif request.method == 'POST':
		if request.form['detection'] == 'start':
			common.send_command('com det start')
		elif request.form['detection'] == 'stop':
			common.send_command('com det stop')
		return redirect(url_for('pages.index'))

@login_required
def get_det_image(det_number,img_number):
	filename = '/var/detections/%s/capture_%s.jpeg' % (det_number,img_number)
	print(filename)
	return send_file(filename, mimetype='image/png', add_etags=False, cache_timeout=0)


@login_required
def liveview():
	if request.method == 'GET':
		ret = common.send_command('req lvw status')
		if ret[0] == 1:
			return render_template('error.html')
		lvw_started_str = ret[1]
		if lvw_started_str == 'yes':
			lvw_started = True
		else:
			lvw_started = False
		print('det started %d' % (lvw_started))
		return render_template('liveview.html',lvw_started=lvw_started)
	elif request.method == 'POST':
		if request.form['liveview'] == 'start':
			common.send_command('com lvw start')
		elif request.form['liveview'] == 'stop':
			common.send_command('com lvw stop')
		return redirect(url_for('pages.liveview'))

@login_required
def options():
	if request.method == 'GET':
		return render_template('options.html')
	elif request.method == 'POST':
		set_login_pass_hash(request.form['password'])
		with open('/etc/gunicorn/password', 'w') as file:
			file.write(get_login_pass_hash())
		logout_user()
		return 'ok'

def login():
	return render_template('login.html')

@login_required
def logout():
	logout_user()
	return redirect(url_for('pages.login'))


# Routes
routes_pages.add_url_rule('/login', 'login', login, methods=['GET'])
routes_pages.add_url_rule('/logout', 'logout', logout, methods=['GET', 'POST'])
routes_pages.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
routes_pages.add_url_rule('/liveview', 'liveview', liveview, methods=['GET', 'POST'])
routes_pages.add_url_rule('/options', 'options', options, methods=['GET', 'POST'])
routes_pages.add_url_rule('/detection/<det_number>/<img_number>', 'get_det_image', get_det_image, methods=['GET'])


