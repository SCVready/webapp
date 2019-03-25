from flask import Flask, render_template, request, abort, redirect, url_for, Response, g, send_file
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit, disconnect
import os, sys, socket, time, random, errno, functools
from threading import Lock, Thread
from time import sleep
from common import send_command

thread = None
thread_lock = Lock()

jpeg = None
async_mode = None
new_frame = False;

app = Flask(__name__)
app.config['SECRET_KEY'] = "ruyi618touipí043ewd" # a secret key for your app TODO rnd generation on init.d

#LOGIN CONF
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#SOCKETIO CONF
socketio = SocketIO(app, async_mode=async_mode, manage_session=False)


def authenticated_only(f):
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		if not current_user.is_authenticated:
			disconnect()
		else:
			return f(*args, **kwargs)
	return wrapped

def threaded_function():
	global jpeg
	global new_frame
	pipe_path = '/run/kinectalarm/liveview_frames_pipe'
	counter = 0
	try:
		os.mkfifo(pipe_path)
	except OSError as oe:
		if oe.errno != errno.EEXIST:
			raise

	while True:
		new_pipe = os.open(pipe_path,os.O_RDONLY)
		while True:
			data_0 = os.read(new_pipe,9)
			bytes_read = len(data_0)
			if bytes_read == 0:
				break
			
			data_1 = os.read(new_pipe,4)
			bytes_read = len(data_1)
			if bytes_read == 0:
				break
			size_load = int.from_bytes(data_1, byteorder='little')
			counter = counter + 1
			
			bytes_to_read = size_load;
			jpeg = b''
			while bytes_to_read > 0:
				data_3 = os.read(new_pipe,bytes_to_read)
				bytes_read = len(data_3)
				if bytes_read == 0:
					break
				jpeg += data_3
				bytes_to_read -=bytes_read
			if bytes_to_read != 0:
				break;
			data_4 = os.read(new_pipe,9)
			bytes_read = len(data_4)
			if bytes_read == 0:
				break
			new_frame = True

def background_thread():
	global new_frame
	thread2 = Thread(target = threaded_function)
	thread2.daemon = True
	thread2.start()
	while True:
		if new_frame:
			socketio.emit('my event', {'frame': jpeg})
			new_frame = False
		socketio.sleep(0.05)

@socketio.on('my event')
@authenticated_only
def connect(json):
	global thread
	with thread_lock:
		if thread is None:
			thread = socketio.start_background_task(background_thread)

@login_manager.user_loader
def load_user(user_id):
	return User(user_id)

class User(UserMixin):
	def __init__(self,id):
		self.id = id
		
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
	if request.method == 'GET':
		ret = send_command('req det status')
		if ret[0] == 1:
			return render_template('error.html')
		det_started_str = ret[1]
		if det_started_str == 'yes':
			det_started = True
		else:
			det_started = False
		print('det started %d' % (det_started))
		ret = send_command('req det num')
		if ret[0] == 1:
			return render_template('error.html')
		det_num = int(ret[1])
		return render_template('main.html',det_started=det_started,det_num=det_num)
	elif request.method == 'POST':
		if request.form['detection'] == 'start':
			send_command('com det start')
		elif request.form['detection'] == 'stop':
			send_command('com det stop')
		return redirect(url_for('index'))
		
@app.route('/detection/<det_number>/<img_number>')
@login_required
def get_det_image(det_number,img_number):
	filename = '/var/detections/%s/capture_%s.jpeg' % (det_number,img_number)
	print(filename)
	return send_file(filename, mimetype='image/png', add_etags=False, cache_timeout=0)

@app.route('/reset_detection', methods=['POST'])
@login_required
def reset_detection():
	if request.form['delete_detections'] == 'true':
		send_command('com det rst')
	return redirect(url_for('index'))

@app.route("/liveview", methods=['GET', 'POST'])
@login_required
def liveview():
	if request.method == 'GET':
		ret = send_command('req lvw status')
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
			send_command('com lvw start')
		elif request.form['liveview'] == 'stop':
			send_command('com lvw stop')
		return redirect(url_for('liveview'))

@app.route("/api/det_status", methods=['GET', 'POST'])
@login_required
def api_det_status():
	if request.method == 'GET':
		ret = send_command('req det status')
		if ret[0] == 1:
			return 'error'
		det_started_str = ret[1]
		if det_started_str == 'yes':
			det_started = True
		else:
			det_started = False
		return str(det_started)
	elif request.method == 'POST':
		if request.form['det'] == 'start':
			send_command('com det start')
		elif request.form['det'] == 'stop':
			send_command('com det stop')
		return 'ok'

@app.route("/api/lvw_status", methods=['GET', 'POST'])
@login_required
def api_lvw_status():
	if request.method == 'GET':
		ret = send_command('req lvw status')
		if ret[0] == 1:
			return 'error'
		lvw_started_str = ret[1]
		if lvw_started_str == 'yes':
			lvw_started = True
		else:
			lvw_started = False
		return str(lvw_started)
	elif request.method == 'POST':
		if request.form['det'] == 'start':
			send_command('com lvw start')
		elif request.form['det'] == 'stop':
			send_command('com lvw stop')
		return 'ok'

@app.route('/login', methods=['GET'])
def login():
	return render_template('login.html')
	
@app.route('/request_login', methods=['POST'])
def request_login():
	if request.form['password'] == 'pass':
		login_user(User(1))
	else:
		rand_wait_time = random.uniform(2,4)
		time.sleep(rand_wait_time)
	return redirect(url_for('index'))
	
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
