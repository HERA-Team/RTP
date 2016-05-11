'''
rtp.site.flask_app

author | Immanuel Washington

Functions
---------
monitor_app | creates flask app for monitor db
monitor_lm | creates login manager for monitor db
monitor_db | creates monitor db from sqlalchemy
'''
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

monitor_app = Flask(__name__, static_folder='monitor/static', template_folder='monitor/templates')
monitor_app.config.from_pyfile('monitor/settings.py')

monitor_lm = LoginManager()
monitor_lm.init_app(monitor_app)

monitor_db = SQLAlchemy(monitor_app)
