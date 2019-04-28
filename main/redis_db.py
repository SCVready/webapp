
import redis

class redis_database:
	def __init__(self):
		self.r = None
		self.p = None

	def connect(self):
		if not self.r:
			self.r = redis.Redis(unix_socket_path='/tmp/redis.sock')
			self.p = self.r.pubsub()

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

redis_db = redis_database()
