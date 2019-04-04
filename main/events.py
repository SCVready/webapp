from flask_login import current_user
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock, Thread
from time import sleep
import os, sys, socket, time, random, errno, functools, hashlib ,base64

from .. import socketio

thread = None
thread_lock = Lock()
jpeg = b''
new_frame = False

def authenticated_only(f):
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		if not current_user.is_authenticated:
			disconnect()
		else:
			return f(*args, **kwargs)
	return wrapped

def from_bytes (data, big_endian = False):
    if isinstance(data, str):
        data = bytearray(data)
    if big_endian:
        data = reversed(data)
    num = 0
    for offset, byte in enumerate(data):
        num += byte << (offset * 8)
    return num

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
			size_load = from_bytes(data_1, False) # int.from_bytes(data_1, byteorder='little')		
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
			jpeg_base64 = base64.b64encode(jpeg)	
			socketio.emit('my event', {'frame': jpeg_base64})
			new_frame = False
		socketio.sleep(0.05)

@socketio.on('my event')
@authenticated_only
def connect(json):
	global thread
	with thread_lock:
		if thread is None:
			thread = socketio.start_background_task(background_thread)

