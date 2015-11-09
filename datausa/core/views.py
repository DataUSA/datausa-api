from flask import Blueprint, request, jsonify
from datausa.attrs.models import Cip, Naics, University
from datausa.core import table_manager
from datausa.core import api
from datausa.core.models import ApiObject
from datausa.core.crosswalker import crosswalk

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
    exclude = request.args.get("exclude", None)

    shows = show.split(",")
    sumlevels = sumlevel.split(",")
    values = required.split(",") if required else [] 

    shows_and_levels = {val:sumlevels[idx] for idx, val in enumerate(shows)}

    variables = manager.possible_variables
    vars_and_vals = {var:request.args.get(var, None) for var in variables}
    vars_and_vals = {k:v for k,v in vars_and_vals.items() if v}


    vars_needed = vars_and_vals.keys() + shows + values
    api_obj = ApiObject(vars_needed=vars_needed, vars_and_vals=vars_and_vals,
                        shows_and_levels=shows_and_levels, values=values,
                        where=where, force=force, order=order,
                        sort=sort, limit=limit, exclude=exclude)
    return api_obj

@mod.route("/")
def api_view():
    api_obj = build_api_obj()
    table_list = manager.all_tables(api_obj)
    table = manager.select_best(table_list, api_obj)
    api_obj.capture_logic(table_list)
    api_obj = manager.crosswalk(table, api_obj)
    data = api.query(table, api_obj)

    return data

@mod.route("/logic/")
def logic_view():
    api_obj = build_api_obj()
    table_list = manager.all_tables(api_obj)
    return jsonify(tables=[table.info() for table in table_list])
