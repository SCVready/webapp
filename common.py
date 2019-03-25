import os, sys, socket, time, random, errno, functools

def send_command(comm):
	server_address = "/run/kinectalarm/kinect_alarm_socket"
	print('connecting to {}'.format(server_address))
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
	try:
		sock.connect(server_address)
	except socket.error as msg:
		return (1,'0')
	try:
		# Send data
		message = str.encode(comm)
		print('sending {!r}'.format(message))
		sock.sendall(message)
		data = sock.recv(56)
		print('received {!r}'.format(data))

	finally:
		print('closing socket')
		sock.close()
		
	return (0,data.decode())
