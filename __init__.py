from flask import Flask, Blueprint, render_template
from flask_login import LoginManager
from flask_socketio import SocketIO, emit, disconnect

# GLOBAL VARIABLES
async_mode = None
app = Flask(__name__)

with open("/etc/gunicorn/webapp-key") as f:
    flask_key = f.read()
app.config['SECRET_KEY'] = flask_key

# LOGIN CONF
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'pages.login'
import main.auth

# ADD ROUTES TO APP
from main.pages import routes_pages
from main.services import routes_services
app.register_blueprint(routes_pages)
app.register_blueprint(routes_services)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# SOCKETIO CONF
socketio = SocketIO(app, async_mode=async_mode, manage_session=False)
from main.events import background_thread,background_thread_system_info
socketio.start_background_task(background_thread)
socketio.start_background_task(background_thread_system_info)

# Component initialization
from main.auth import initialize_auth
from main.redis_db import redis_db
from main.sqlite_db import sqlite_db

@app.before_first_request
def initialice_server():
	initialize_auth()
	redis_db.connect();
	redis_db.set_var('ssh_activate','0')#TODO temp
	redis_db.set_var('presenceos_version','0.1')
	redis_db.set_var('webapp_version','0.1')
	sqlite_db.connect();

# JINJA FILTERS
from datetime import datetime
def format_datetime(value):
    ts = int(value)
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S UTC')

app.jinja_env.filters['datetime'] = format_datetime


app.jinja_env.filters['datetime'] = format_datetime

