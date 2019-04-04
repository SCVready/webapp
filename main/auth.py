from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from .. import login_manager


login_pass_hash = None

def get_login_pass_hash():
	global login_pass_hash
	return login_pass_hash

def set_login_pass_hash(new_login_pass_hash):
	global login_pass_hash
	login_pass_hash = new_login_pass_hash

def initialize_auth():
	global login_pass_hash;
	with open('/etc/gunicorn/password', 'r') as content_file:
		content = content_file.read()
	login_pass_hash = content.rstrip()
	print(login_pass_hash)
	

class User(UserMixin):
	def __init__(self,id):
		self.id = id

@login_manager.user_loader
def load_user(user_id):
	return User(user_id)
