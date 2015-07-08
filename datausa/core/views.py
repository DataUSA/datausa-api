from flask import Blueprint, request, jsonify
from datausa.attrs.models import Course, Naics, University
from datausa.core import table_manager
from datausa.core import api
from datausa.core.models import ApiObject

mod = Blueprint('core', __name__, url_prefix='/api')

manager = table_manager.TableManager()

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = [a.serialize() for a in attrs]
    return jsonify(data=data)

def build_api_obj():
    show = request.args.get("show", "")
    sumlevel = request.args.get("sumlevel", "")
    required = request.args.get("required", "")

    shows = show.split(",")
    sumlevels = sumlevel.split(",")
    values = required.split(",") if required else [] 

    shows_and_levels = {val:sumlevels[idx] for idx, val in enumerate(shows)}

    variables = manager.possible_variables
    vars_and_vals = {var:request.args.get(var, None) for var in variables}
    vars_and_vals = {k:v for k,v in vars_and_vals.items() if v}


    vars_needed = vars_and_vals.keys() + [show] + values
    api_obj = ApiObject(vars_needed=vars_needed, vars_and_vals=vars_and_vals,
                        shows_and_levels=shows_and_levels, values=values)
    return api_obj

@mod.route("/")
def api_view():
    api_obj = build_api_obj()
    table = manager.find_table(api_obj.vars_needed, api_obj.shows_and_levels)
    data = api.query(table, api_obj.vars_and_vals, api_obj.shows_and_levels, values=api_obj.values)

    return data

@mod.route("/logic/")
def logic_view():
    api_obj = build_api_obj()
    table_list = manager.all_tables(api_obj.vars_needed, api_obj.shows_and_levels)
    return jsonify(tables=[table.info() for table in table_list])