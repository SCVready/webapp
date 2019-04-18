
import redis

class redis_connection:
	def __init__(self):
		self.r = None

	def connect(self):
		self.r = redis.Redis(host='localhost', port=6379, db=0)

	def set_var(self,var,value):
		return self.r.set(var,value)

	def get_var(self,var):
		return self.r.get(var)

redis_con = redis_connection()

def initialize_db():
	redis_con.connect()
