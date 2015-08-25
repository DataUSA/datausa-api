import flask
import sqlalchemy

from datausa.core import get_columns
from datausa.attrs import consts

def simple_format(cols, data):
    headers = [col if isinstance(col, basestring) else col.key for col in cols]
    data = {
            "headers": list(headers),
            "data": [ list(row) for row in data]
    }
    return flask.jsonify(data)

def parse_method_and_val(cond):
    if cond.startswith("^"):
        return "startswith", cond[1:]
    elif cond.endswith("$"):
        return "endswith", cond[:-1]
    else:
        return "like", cond

def where_filters(table, where_str):
    filts = []
    wheres = where_str.split(",")
    for where in wheres:
        colname, cond = where.split(":")
        col = getattr(table, colname)
        method, value = parse_method_and_val(cond)
        filts.append(getattr(col, method)(value))
    return filts

def query(table, api_obj): #vars_and_vals, shows_and_levels, values=[]):
    vars_and_vals = api_obj.vars_and_vals
    shows_and_levels = api_obj.shows_and_levels
    values = api_obj.values if hasattr(api_obj, "values") else []

    filters = [ getattr(table, var) == val for var,val in vars_and_vals.items() ]
    filters += where_filters(table, api_obj.where)
    # if values:
    #     pk = [col for col in table.__table__.columns if col.primary_key]
    #     cols = pk + values
    # else:
    cols = get_columns(table)

    needs_show_filter = any([v != consts.ALL for v in shows_and_levels.values()])

    if needs_show_filter and hasattr(table, "gen_show_level_filters"):
        filters += table.gen_show_level_filters(shows_and_levels)

    data = table.query.with_entities(*cols).filter(*filters).all()    
    return simple_format(cols, data)
