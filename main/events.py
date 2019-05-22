from flask_login import current_user
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock, Thread
from time import sleep
import os, sys, socket, time, random, errno, functools, hashlib ,base64

import common
import psutil
import shutil
import os
import json

from .. import socketio
from redis_db import redis_db

thread = None
thread_lock = Lock()

def authenticated_only(f):
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		if not current_user.is_authenticated:
			disconnect()
		else:
			return f(*args, **kwargs)
	return wrapped

def background_thread_system_info():
	redis_db.connect()
	
	while True:
		cpu = psutil.cpu_percent()
		ram = psutil.virtual_memory()[2]
	
		stats = os.statvfs('/')
		total = stats.f_frsize * stats.f_blocks
		free = stats.f_frsize * stats.f_bavail
		used = total - free
		disk = float(used)/float(total)*100

		data = {
		"cpu": cpu,
		"ram": ram,
		"disk": disk}
		redis_db.publish("system_info",json.dumps(data))
		socketio.sleep(1)

def background_thread():
	redis_db.connect()
	redis_db.subscribe('liveview')
	redis_db.subscribe('new_det')
	redis_db.subscribe('system_info')

	redis_db.subscribe('event_default')
	redis_db.subscribe('event_success')
	redis_db.subscribe('event_error')
	redis_db.subscribe('event_warning')
	redis_db.subscribe('event_info')

	while True:
		message = redis_db.get_message()
		if message and message['type'] == 'pmessage':
			if message['channel'] == 'liveview':
				socketio.emit('liveview', {'frame': message['data']}, namespace='/liveview')

			elif message['channel'] == 'event_default':
				socketio.emit('default', {'content': message['data']}, namespace='/events')
			elif message['channel'] == 'event_success':
				socketio.emit('success', {'content': message['data']}, namespace='/events')
			elif message['channel'] == 'event_error':
				socketio.emit('error', {'content': message['data']}, namespace='/events')
			elif message['channel'] == 'event_warning':
				socketio.emit('warning', {'content': message['data']}, namespace='/events')
			elif message['channel'] == 'event_info':
				socketio.emit('info', {'content': message['data']}, namespace='/events')

			elif message['channel'] == 'new_det':
				socketio.emit('newdet', {'event': message['data']}, namespace='/detections')
			elif message['channel'] == 'system_info':
				data = json.loads(message['data'])
				socketio.emit('system_info', {'cpu': data['cpu'],'ram': data['ram'],'disk': data['disk']}, namespace='/system_info')
		else:
			socketio.sleep(0.05)

@socketio.on('connect', namespace='/liveview')
@authenticated_only
def connect():
	print("liveview")

@socketio.on('connect', namespace='/events')
@authenticated_only
def connect():
	print("events")
