
import sqlite3

class sqlite_database:
	def __init__(self):
		self.con = None

	def connect(self):
		if not self.con:
			self.con = sqlite3.connect('/etc/kinectalarm/detections.db')

	def get_number_detections(self):
		cur = self.con.cursor()
		cur.execute('SELECT count(*) FROM detections')
		return cur.fetchone()[0]

	def get_detecions(self):
		cur = self.con.cursor()
		cur.execute('SELECT * FROM detections')
		return cur.fetchall()

	def get_detecions_filename(self,number):
		cur = self.con.cursor()
		cur.execute('SELECT FILENAME FROM detections WHERE id={}'.format(number))
		return cur.fetchone()[0]

sqlite_db = sqlite_database()
