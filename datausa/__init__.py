import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from datausa.attrs.views import mod as attrs_module
from datausa.ipeds.views import mod as ipeds_module
app.register_blueprint(attrs_module)
app.register_blueprint(ipeds_module)
