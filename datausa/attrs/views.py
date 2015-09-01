from datausa import app
from flask import Blueprint, request, jsonify

mod = Blueprint('attrs', __name__, url_prefix='/attrs')
from datausa.attrs.models import Cip, Naics, University, Soc, Degree
from datausa.attrs.models import Skill, Sector, Geo

attr_map = {"soc": Soc, "naics" : Naics, "cip": Cip,
            "geo": Geo, "university": University, "degree": Degree,
            "skill": Skill, "sector": Sector}

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = [a.serialize() for a in attrs]
    return jsonify(data=data)

@mod.route("/<kind>/")
def attrs(kind):

    if kind in attr_map:
        attr_obj = attr_map[kind]
        return show_attrs(attr_obj)
    raise Exception("Invalid attribute type.")

@mod.route("/<kind>/<attr_id>/")
def attr_id(kind, attr_id):

    if kind in attr_map:
        attr_obj = attr_map[kind]
        aid_obj = attr_obj.query.get(attr_id)
        return jsonify(data=aid_obj.serialize())
    raise Exception("Invalid attribute type.")

app.register_blueprint(mod)