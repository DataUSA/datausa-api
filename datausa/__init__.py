import os
from flask import Flask
from flask.ext.compress import Compress
from flask.ext.cors import CORS
from flask.ext.cache import Cache

app = Flask(__name__)
app.config.from_object('config')
Compress(app)

from datausa.attrs.views import mod as attrs_module
from datausa.core.views import mod as core_module

app.register_blueprint(attrs_module)
app.register_blueprint(core_module)
CORS(app)

cache = Cache(app)

from datausa.core.table_manager import TableManager
manager = TableManager()
