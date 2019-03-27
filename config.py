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
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_SIZE = 15
SQLALCHEMY_POOL_TIMEOUT = 180
SQLALCHEMY_POOL_RECYCLE = 150
SQLALCHEMY_DATABASE_URI = "postgres://{0}:{1}@{2}:{3}/{4}".format(
    os.environ.get("DATAUSA_DB_USER", "postgres"),
    os.environ.get("DATAUSA_DB_PW", ""),
    os.environ.get("DATAUSA_DB_HOST", "localhost"),
    os.environ.get("DATAUSA_DB_PORT", 5432),
    os.environ.get("DATAUSA_DB_NAME", "postgres"))

''' If an env var for production is set turn off all debugging support '''
if "DATAUSA_PRODUCTION" in os.environ:
    SQLALCHEMY_ECHO = False
    DEBUG = False
    ERROR_EMAIL = True

JSONIFY_PRETTYPRINT_REGULAR = False

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(basedir, 'cache/')
CACHE_DEFAULT_TIMEOUT = os.environ.get("CACHE_DEFAULT_TIMEOUT", 60 * 60 * 24 * 7 * 4) # 28 days
CACHE_THRESHOLD = 5000

FLICKR_DIR = os.environ.get("DATAUSA_FLICKR_DIR", os.path.join(basedir, '../datausa-site/datausa/static/img/splash'))
SEARCH_INDEX_DIR = os.path.join(basedir, 'search_index/')
VAR_INDEX_DIR = os.path.join(basedir, 'var_index/')
