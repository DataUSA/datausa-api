from datausa import app
from flask import Blueprint, request, jsonify, abort

mod = Blueprint('attrs', __name__, url_prefix='/attrs')
from datausa.attrs.models import Cip, Naics, University, Soc, Degree
from datausa.attrs.models import Race, Search, ZipLookup, GeoNeighbors
from datausa.attrs.models import OccCrosswalk, IndCrosswalk
from datausa.attrs.models import Skill, Sector, Geo, AcsInd, PumsIoCrosswalk
from datausa.attrs.models import PumsDegree, PumsNaics, PumsRace, PumsSoc
from datausa.attrs.models import PumsWage, PumsSex, PumsBirthplace
from datausa.attrs.models import IoCode, AcsOcc, AcsRace, AcsLanguage, Conflict
from datausa.attrs.consts import ALL, GEO, GEO_LEVEL_MAP

from whoosh.qparser import QueryParser
from whoosh import index, sorting, qparser, scoring, query
from config import SEARCH_INDEX_DIR

import re

def to_bool(x):
    return x and x.lower() == "true"

class CWeighting(scoring.Weighting):
    def __init__(self, fullterm):
        self.termweight = scoring.BM25F()
        self.fullterm = fullterm.lower().strip()
    def score(self, searcher, fieldnum, text, docnum, weight, qf=1):
        # Get the BM25 score for this term in this document
        bm25 = self.termweight.scorer(searcher, fieldnum, text, docnum)
        q=qp.parse(text)
        score_me = bm25.score(q.matcher(searcher))
        name = searcher.stored_fields(docnum).get("name")
        zvalue = searcher.stored_fields(docnum).get("zvalue")
        if name == self.fullterm:
            return score_me * 30 + (25 * abs(zvalue))
        elif name.startswith(self.fullterm):
            if zvalue > 0:
                return (score_me * 5.75) + (25 * zvalue)
            else:
                return score_me * 5.75 + (1 - abs(zvalue) * 25)
        elif text.startswith(name):
            return (score_me * 1.75) + (10 * zvalue)
        return (score_me * 0.75) + (zvalue * 0.25)

ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)
facet = sorting.FieldFacet("zvalue", reverse=True)
scores = sorting.ScoreFacet()

attr_map = {"soc": PumsSoc, "naics" : PumsNaics, "cip": Cip,
            "geo": Geo, "university": University, "degree": Degree,
            "skill": Skill, "sector": Sector,
            "pums_degree": PumsDegree,
            "pums_race": PumsRace, "sex": PumsSex,
            "birthplace": PumsBirthplace,
            "wage_bin": PumsWage, "iocode": IoCode,
            "race": Race, "acs_race": AcsRace,
            "acs_occ": AcsOcc, "conflict": Conflict, "acs_ind": AcsInd,
            "language": AcsLanguage,
            "bls_soc": Soc, "bls_naics": Naics}

def show_attrs(attr_obj, sumlevels=None):
    if sumlevels is not None:
        if attr_obj is Geo:
            sumlevels = [GEO_LEVEL_MAP[lvl] if lvl in GEO_LEVEL_MAP else lvl for lvl in sumlevels]
            attrs = attr_obj.query.filter(attr_obj.sumlevel.in_(sumlevels)).all()
        else:
            attrs = attr_obj.query.filter(attr_obj.level.in_(sumlevels)).all()
    elif attr_obj is Geo:
        # exclude census tracts and ZIPs
        attrs = attr_obj.query.filter(~Geo.id.startswith("140"), ~Geo.id.startswith("860")).all()
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
        sumlevel = request.args.get("sumlevel", None)
        sumlevels = sumlevel.split(",") if sumlevel else None
        return show_attrs(attr_obj, sumlevels=sumlevels)
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

@mod.route("/list/")
def attrs_list():
    return jsonify(data=attr_map.keys())

@mod.route("/<kind>/<attr_id>/parents/")
def get_parents(kind, attr_id):
    if kind in attr_map:
        attr_obj = attr_map[kind]
        data, headers = attr_obj.parents(attr_id)
        return jsonify(data=data, headers=headers)
    raise Exception("Invalid attribute type.")


@mod.route("/<kind>/<attr_id>/children/")
def get_children(kind, attr_id):
    if kind in attr_map:
        attr_obj = attr_map[kind]
        kwargs = request.args
        data, headers = attr_obj.children(attr_id, **kwargs)
        return jsonify(data=data, headers=headers)
    raise Exception("Invalid attribute type.")


def do_search(txt, sumlevel=None, kind=None, tries=0, limit=10, is_stem=None):
    my_filter = None
    if kind and sumlevel:
        kf = query.Term("kind", kind)
        sf = query.Term("sumlevel", sumlevel)
        my_filter = query.And([kf, sf])
    elif kind:
        my_filter = query.Term("kind", kind)
    elif sumlevel:
        my_filter = query.Term("sumlevel", sumlevel)
    if is_stem and is_stem > 0 and my_filter is not None:
        my_filter = my_filter & query.NumericRange("is_stem", 1, is_stem)
    elif is_stem and is_stem > 0 and my_filter is None:
        my_filter = query.NumericRange("is_stem", 1, is_stem)

    if tries > 2:
        return [],[],[]
    q = qp.parse(txt)

    with ix.searcher(weighting=CWeighting(txt)) as s:
        if len(txt) > 2:
            corrector = s.corrector("display")
            suggs = corrector.suggest(txt, limit=10, maxdist=2, prefix=3)
        else:
            suggs = []
        results = s.search_page(q, 1, sortedby=[scores], pagelen=20, filter=my_filter)
        data = [[r["id"], r["name"], r["zvalue"],
                 r["kind"], r["display"],
                 r["sumlevel"] if "sumlevel" in r else "",
                 r["is_stem"] if "is_stem" in r else False,
                 r["url_name"] if "url_name" in r else None]
                for r in results]
        if not data and suggs:
            return do_search(suggs[0], sumlevel, kind, tries=tries+1, limit=limit, is_stem=is_stem)
        return data, suggs, tries

@mod.route("/search/")
def search():
    offset = request.args.get("offset", None)
    limit = int(request.args.get("limit", 10))
    kind = request.args.get("kind", None)
    sumlevel = request.args.get("sumlevel", None)
    txt = request.args.get("q", '').lower()
    is_stem = int(request.args.get("is_stem", 0))

    if txt and re.match('^[0-9]{1,5}$', txt):
        return zip_search(txt, limit=limit)
    elif not txt or len(txt) <= 1:
        return search_old()

    data, suggs, tries = do_search(txt, sumlevel, kind, limit=limit, is_stem=is_stem)
    headers = ["id", "name", "zvalue", "kind", "display", "sumlevel", "is_stem", "url_name"]
    autocorrected = tries > 0
    suggs = [x for x in suggs if x != txt]
    return jsonify(data=data, headers=headers, suggestions=suggs, autocorrected=autocorrected)

@mod.route("/search_old/")
def search_old():
    q = request.args.get("q", '')
    q = q.lower()
    offset = request.args.get("offset", None)
    limit = request.args.get("limit", 100)
    kind = request.args.get("kind", None)
    sumlevel = request.args.get("sumlevel", None)
    is_stem = int(request.args.get("is_stem", 0))
    filters = [Search.name.like("%{}%".format(q))]
    if kind:
        filters.append(Search.kind == kind)
    if sumlevel:
        filters.append(Search.sumlevel == sumlevel)
    if is_stem == 1:
        filters.append(Search.is_stem == is_stem)
    elif is_stem == 2:
        filters.append(Search.is_stem >= 1)
    qry = Search.query.filter(*filters).order_by(Search.zvalue.desc())
    if limit:
        qry = qry.limit(int(limit))
    if offset:
        qry = qry.offset(int(offset))
    qry = qry.all()

    data = [[a.id, a.name, a.zvalue, a.kind, a.display, a.sumlevel, a.is_stem, a.url_name] for a in qry]

    headers = ["id", "name", "zvalue", "kind", "display", "sumlevel", "is_stem", "url_name"]
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


def zip_search(zc, limit=10):
    if len(zc) != 5:
        zc += "%"
    zc = "86000US" + zc

    filters = [
        ZipLookup.child_geoid.like(zc),
        ZipLookup.percent_covered >= 90,
        Search.id == ZipLookup.parent_geoid
    ]

    qry = Search.query.join(ZipLookup).filter(*filters)
    qry = qry.order_by(ZipLookup.parent_area.asc())

    qry = qry.with_entities(Search.id, Search.name, Search.zvalue, Search.kind,
                            Search.display, Search.sumlevel, ZipLookup.child_geoid, Search.is_stem, Search.url_name)
    qry = qry.limit(limit)
    data = [list(row) for row in qry]
    headers = ["id", "name", "zvalue", "kind", "display", "sumlevel", "zipcode", "is_stem", "url_name"]
    return jsonify(data=data, headers=headers, zip_search=True)


@mod.route("/geo/<geo_id>/neighbors/")
def neighbors(geo_id):
    results = GeoNeighbors.query.filter_by(geo=geo_id).all()
    headers = ["geo", "neighbor"]
    data = [[result.geo, result.neighbor] for result in results]
    return jsonify(data=data, headers=headers)


@mod.route("/geo/<attr_id>/ipeds/")
def has_ipeds_data(attr_id):
    from datausa.util import inmem
    # first check, do I have any data
    data, headers = Geo.parents(attr_id)
    id_idx = headers.index("id")
    ipeds_places = inmem.ipeds_place_map()
    if attr_id in ipeds_places:
        return jsonify(data=[], headers=[])
    data.reverse()
    for row in data:
        geo_id = row[id_idx]
        if geo_id in ipeds_places:
            return jsonify(data=[geo_id], headers=[GEO])

@mod.route("/crosswalk/<attr_kind>/<attr_id>/")
def crosswalk_acs(attr_kind, attr_id):
    if attr_kind not in ["acs_occ", "acs_ind", "iocode"]:
        return abort(404)
    if attr_kind == "iocode":
        results = PumsIoCrosswalk.query.filter(PumsIoCrosswalk.iocode == attr_id).all()
        results = [[item.pums_naics, "naics"] for item in results]
    else:
        attr_obj = {"acs_occ": OccCrosswalk, "acs_ind": IndCrosswalk}[attr_kind]
        header_name = {"acs_occ": "soc", "acs_ind": "naics"}[attr_kind]
        col_name = "pums_{}".format(header_name)
        results = attr_obj.query.filter(getattr(attr_obj, attr_kind) == attr_id).with_entities(col_name).all()
        results = [[getattr(item, col_name), header_name] for item in results]
    return jsonify(data=results, headers=["attr_id", "attr_kind"])
