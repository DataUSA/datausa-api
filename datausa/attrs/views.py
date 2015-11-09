from datausa import app
from flask import Blueprint, request, jsonify

mod = Blueprint('attrs', __name__, url_prefix='/attrs')
from datausa.attrs.models import Cip, Naics, University, Soc, Degree
from datausa.attrs.models import Race, Search
from datausa.attrs.models import Skill, Sector, Geo, AcsInd
from datausa.attrs.models import PumsDegree, PumsNaics, PumsRace, PumsSoc
from datausa.attrs.models import PumsWage, PumsSex, PumsBirthplace
from datausa.attrs.models import IoCode, AcsOcc, AcsRace, AcsLanguage, Conflict
from datausa.attrs.consts import ALL

from whoosh.qparser import QueryParser
from whoosh import index, sorting, qparser
from config import SEARCH_INDEX_DIR

ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)
facet = sorting.FieldFacet("zvalue", reverse=True)


attr_map = {"soc": PumsSoc, "naics" : PumsNaics, "cip": Cip,
            "geo": Geo, "university": University, "degree": Degree,
            "skill": Skill, "sector": Sector,
            "pums_degree": PumsDegree,
            "pums_race": PumsRace, "sex": PumsSex,
            "birthplace": PumsBirthplace,
            "wage_bin": PumsWage, "iocode": IoCode,
            "race": Race, "acs_race": AcsRace,
            "acs_occ": AcsOcc, "conflict": Conflict, "acs_ind": AcsInd,
            "language": AcsLanguage}

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
        if kind in ["naics", "soc"]:
            aid_obj = attr_obj.query.filter_by(id=attr_id).order_by(attr_obj.level.asc()).first()
        else:
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

def do_search(txt, sumlevel=None, kind=None, tries=0):
    if kind:
        txt += " AND kind:{}".format(kind)
    if sumlevel:
        txt += " AND sumlevel:{}".format(sumlevel)
    if tries > 2:
        return [],[]
    q = qp.parse(txt)

    with ix.searcher() as s:
        corrector = s.corrector("display")
        suggs = corrector.suggest(txt, limit=10, maxdist=2, prefix=3)
        results = s.search(q, sortedby=facet)
        data = [[r["id"], r["name"], r["zvalue"],
                 r["kind"], r["display"], r["sumlevel"]]
                for r in results]
        if not data and suggs:
            return do_search(suggs[0], sumlevel, kind, tries=tries+1)
        return data, suggs

@mod.route("/search/")
def search():
    offset = request.args.get("offset", None)
    limit = request.args.get("limit", 100)
    kind = request.args.get("kind", None)
    sumlevel = request.args.get("sumlevel", None)
    txt = request.args.get("q", '')
    if not txt:
        return search_old()

    data, suggs = do_search(txt, sumlevel, kind)
    headers = ["id", "name", "zvalue", "kind", "display", "sumlevel"]
    return jsonify(data=data, headers=headers, suggestions=suggs)

@mod.route("/search_old/")
def search_old():
    q = request.args.get("q", '')
    q = q.lower()
    offset = request.args.get("offset", None)
    limit = request.args.get("limit", 100)
    kind = request.args.get("kind", None)
    sumlevel = request.args.get("sumlevel", None)
    filters = [Search.name.like("%{}%".format(q))]
    if kind:
        filters.append(Search.kind == kind)
    if sumlevel:
        filters.append(Search.sumlevel == sumlevel)
    qry = Search.query.filter(*filters).order_by(Search.zvalue.desc())
    if limit:
        qry = qry.limit(int(limit))
    if offset:
        qry = qry.offset(int(offset))
    qry = qry.all()
    data = [[a.id, a.name, a.zvalue, a.kind, a.display, a.sumlevel] for a in qry]
    headers = ["id", "name", "zvalue", "kind", "display", "sumlevel"]
    return jsonify(data=data, headers=headers)


@mod.route("/ranks/")
def ranks():
    attr_sumlvls = {
        "soc": {"0": 6, "1": 17, "2": 24, "3": 478},
        "naics": {"0": 14, "1": 21, "2": 266},
        "cip": {"2": 38, "4": 368, "6": 1416},
        "geo": {"nation": 1,
                "state": 52,
                "county": 3221,
                "msa": 929,
                "place": 29509,
                "puma": 2378}
    }
    return jsonify(data=attr_sumlvls)
