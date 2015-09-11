from datausa import app
from flask import Blueprint, request, jsonify

mod = Blueprint('attrs', __name__, url_prefix='/attrs')
from datausa.attrs.models import Cip, Naics, University, Soc, Degree
from datausa.attrs.models import Skill, Sector, Geo
from datausa.attrs.models import PumsDegree, PumsNaics, PumsRace, PumsSex, PumsBirthplace

attr_map = {"soc": Soc, "naics" : Naics, "cip": Cip,
            "geo": Geo, "university": University, "degree": Degree,
            "skill": Skill, "sector": Sector,
            "pums_degree": PumsDegree,
            "race": PumsRace, "sex": PumsSex,
            "birthplace": PumsBirthplace }

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = []
    headers= []
    for a in attrs:
        obj = a.serialize()
        data.append(obj.values())
        if not headers:
            headers = obj.keys()
    return jsonify(data=data, headers=headers)

@mod.route("/pums/<kind>/")
def pums_attrs(kind):
    return attrs("pums_{}".format(kind))

@mod.route("/pums/<kind>/<attr_id>/")
def pums_attr_id(kind):
    return attr_id("pums_{}".format(kind), attr_id)

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
        tmp = aid_obj.serialize()
        return jsonify(data=[tmp.values()], headers=tmp.keys())
    raise Exception("Invalid attribute type.")

