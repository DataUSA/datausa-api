from datausa import app
from flask import Blueprint, request, jsonify

mod = Blueprint('attrs', __name__, url_prefix='/attrs')
from datausa.attrs.models import Cip, Naics, University, Soc, Degree
from datausa.attrs.models import Race
from datausa.attrs.models import Skill, Sector, Geo
from datausa.attrs.models import PumsDegree, PumsNaics, PumsRace, PumsSoc
from datausa.attrs.models import PumsWage, PumsSex, PumsBirthplace
from datausa.attrs.models import IoCode, AcsOcc

attr_map = {"soc": PumsSoc, "naics" : PumsNaics, "cip": Cip,
            "geo": Geo, "university": University, "degree": Degree,
            "skill": Skill, "sector": Sector,
            "pums_degree": PumsDegree,
            "pums_race": PumsRace, "sex": PumsSex,
            "birthplace": PumsBirthplace,
            "wage_bin": PumsWage, "iocode": IoCode,
            "race": Race,
            "acs_occ": AcsOcc}

def show_attrs(attr_obj):
    if attr_obj is Geo:
        # exclude census tracts
        attrs = attr_obj.query.filter(~Geo.id.startswith("140")).all()
    else:
        attrs = attr_obj.query.all()

    data = []
    headers = []
    for a in attrs:
        obj = a.serialize()
        data.append(obj.values())
        if not headers:
            headers = obj.keys()
    return jsonify(data=data, headers=headers)

@mod.route("/pums/<kind>/")
def pums_attrs(kind):
    return attrs("pums_{}".format(kind))

@mod.route("/pums/<kind>/<pums_attr_id>/")
def pums_attr_id(kind, pums_attr_id):
    return attrs_by_id("pums_{}".format(kind), pums_attr_id)

@mod.route("/<kind>/")
def attrs(kind):

    if kind in attr_map:
        attr_obj = attr_map[kind]
        return show_attrs(attr_obj)
    raise Exception("Invalid attribute type.")

@mod.route("/<kind>/<attr_id>/")
def attrs_by_id(kind, attr_id):

    if kind in attr_map:
        attr_obj = attr_map[kind]
        aid_obj = attr_obj.query.get(attr_id)
        tmp = aid_obj.serialize()
        return jsonify(data=[tmp.values()], headers=tmp.keys())
    raise Exception("Invalid attribute type.")

@mod.route("/list")
def attrs_list():
    return jsonify(data=attr_map.keys())

@mod.route("/<kind>/<attr_id>/parents")
def get_parents(kind, attr_id):
    if kind in attr_map:
        attr_obj = attr_map[kind]
        data, headers = attr_obj.parents(attr_id)
        return jsonify(data=data, headers=headers)
    raise Exception("Invalid attribute type.")

@mod.route("/<kind>/<attr_id>/children")
def get_children(kind, attr_id):
    if kind in attr_map:
        attr_obj = attr_map[kind]
        kwargs = request.args
        data, headers = attr_obj.children(attr_id, **kwargs)
        return jsonify(data=data, headers=headers)
    raise Exception("Invalid attribute type.")
