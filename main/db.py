
import redis

class redis_connection:
	def __init__(self):
		self.r = None
		self.p = None
		self.init = False

	def connect(self):
		self.r = redis.Redis(unix_socket_path='/tmp/redis.sock')
		self.p = self.r.pubsub()
		self.init = True

	def set_var(self,var,value):
		return self.r.set(var,value)

	def get_var(self,var):
		return self.r.get(var)
	
	def publish(self,channel,message):
		self.r.publish(channel, message)

	def subscribe(self,channel):
		self.p.psubscribe(channel)

	def get_message(self):
		return self.p.get_message()

redis_con = redis_connection()

def initialize_db():
	if not redis_con.init:
		redis_con.connect()
