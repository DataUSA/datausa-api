from flask import Blueprint, request, jsonify
from datausa.attrs.models import Cip, Naics, University
from datausa.core import table_manager
from datausa.core import api, join_api
from datausa.core.models import ApiObject
from datausa.core.crosswalker import crosswalk
from datausa.util.big_places import is_big_geo

mod = Blueprint('core', __name__, url_prefix='/api')

manager = table_manager.TableManager()

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = [a.serialize() for a in attrs]
    return jsonify(data=data)

def build_api_obj():
    show = request.args.get("show", "")
    sumlevel = request.args.get("sumlevel", "").lower()
    required = request.args.get("required", "")
    force = request.args.get("force", "")
    where = request.args.get("where", "")
    order = request.args.get("order", "")
    sort = request.args.get("sort", "")
    limit = request.args.get("limit", None)
    offset = request.args.get("offset", None)
    exclude = request.args.get("exclude", None)
    auto_crosswalk = request.args.get("auto_crosswalk", False)
    display_names = request.args.get("display_names", False)

    shows = show.split(",")
    sumlevels = sumlevel.split(",")
    if shows and not sumlevel:
        sumlevels = ["all" for show in shows]
    values = required.split(",") if required else []

    shows_and_levels = {val:sumlevels[idx] for idx, val in enumerate(shows)}

    variables = manager.possible_variables
    vars_and_vals = {var:request.args.get(var, None) for var in variables}
    vars_and_vals = {k:v for k,v in vars_and_vals.items() if v}


    vars_needed = vars_and_vals.keys() + shows + values
    api_obj = ApiObject(vars_needed=vars_needed, vars_and_vals=vars_and_vals,
                        shows_and_levels=shows_and_levels, values=values,
                        where=where, force=force, order=order,
                        sort=sort, limit=limit, exclude=exclude,
                        auto_crosswalk=auto_crosswalk,
                        display_names=display_names,
                        offset=offset)
    return api_obj

@mod.route("/")
@mod.route("/v1/")
@mod.route("/csv/", defaults={'csv': True})
def api_view(csv=None):
    api_obj = build_api_obj()
    api_obj = manager.force_1yr_for_big_places(api_obj)
    api_obj = manager.schema_selector(api_obj)
    table_list = manager.all_tables(api_obj)
    table = manager.select_best(table_list, api_obj)
    api_obj.capture_logic(table_list)
    api_obj = manager.crosswalk(table, api_obj)
    data = api.query(table, api_obj, stream=csv)
    return data

@mod.route("/join/")
@mod.route("/join/csv/", defaults={'csv': True})
def api_join_view(csv=None):
    api_obj = build_api_obj()
    tables = manager.required_tables(api_obj)
    data = join_api.joinable_query(tables, api_obj, manager.table_years, csv_format=csv)
    return data


@mod.route("/logic/")
def logic_view():
    api_obj = build_api_obj()
    table_list = manager.all_tables(api_obj)
    return jsonify(tables=[table.info(api_obj) for table in table_list])
