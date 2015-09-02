# -*- coding: utf-8 -*-
import os

''' Base directory of where the site is held '''
basedir = os.path.abspath(os.path.dirname(__file__))

''' CSRF (cross site forgery) for signing POST requests to server '''
CSRF_EN = True

''' Secret key should be set in environment var '''
SECRET_KEY = os.environ.get("DATAVIVA_SECRET_KEY", "default-datausa-secret")

''' Default debugging to True '''
DEBUG = True
SQLALCHEMY_ECHO = True

SQLALCHEMY_DATABASE_URI = "postgres://{0}:{1}@{2}/{3}".format(
    os.environ.get("DATAUSA_DB_USER", "postgres"),
    os.environ.get("DATAUSA_DB_PW", ""),
    os.environ.get("DATAUSA_DB_HOST", "localhost"),
    os.environ.get("DATAUSA_DB_NAME", "postgres"))

''' If an env var for production is set turn off all debugging support '''
if "DATAUSA_PRODUCTION" in os.environ:
    SQLALCHEMY_ECHO = False
    DEBUG = False
    ERROR_EMAIL = True

JSONIFY_PRETTYPRINT_REGULAR = False