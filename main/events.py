from flask_login import current_user
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock, Thread
from time import sleep
import os, sys, socket, time, random, errno, functools, hashlib ,base64

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

def background_thread():
	redis_db.connect()
	redis_db.subscribe('liveview')
	redis_db.subscribe('kinectalarm_event')
	while True:
		message = redis_db.get_message()
		if message and message['type'] == 'pmessage':
			if message['channel'] == 'liveview':
				socketio.emit('liveview', {'frame': message['data']}, namespace='/liveview')
			if message['channel'] == 'kinectalarm_event':
				socketio.emit('kinectalarm_event', {'event': message['data']}, namespace='/events')
		socketio.sleep(0.05)

@socketio.on('connect', namespace='/liveview')
@authenticated_only
def connect():
	print("liveview")

@socketio.on('connect', namespace='/events')
@authenticated_only
def connect():
	print("events")
