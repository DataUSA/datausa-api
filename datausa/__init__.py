import os
from flask import Flask, jsonify
from flask.ext.compress import Compress
# from flask.ext.cors import CORS
from flask.ext.cache import Cache

app = Flask(__name__)
app.config.from_object('config')
Compress(app)
cache = Cache(app)

from datausa.attrs.views import mod as attrs_module
from datausa.core.views import mod as core_module

app.register_blueprint(attrs_module)
app.register_blueprint(core_module)

app.url_map.strict_slashes = False

# CORS(app)

@app.errorhandler(500)
def error_page(err):
    return jsonify(error=str(err)), 500
