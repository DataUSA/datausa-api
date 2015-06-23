from datausa import app
from datausa.core import api
from flask import Blueprint, request, jsonify

mod = Blueprint('ipeds', __name__, url_prefix='/ipeds')
from datausa.ipeds.models import GradsYucd

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = [a.serialize() for a in attrs]
    return jsonify(data=data)

@mod.route("/")
def ipeds():
    filters = [ getattr(GradsYucd, key) == value  for key,value in request.args.items() ]
    cols = GradsYucd.__table__.columns
    data = GradsYucd.query.with_entities(*cols).filter(*filters).all()
    return api.simple_format(cols, data)
