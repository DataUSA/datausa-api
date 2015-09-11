import flask
import sqlalchemy

from datausa.core import get_columns
from datausa.attrs import consts

def simple_format(table, cols, data, subs):
    headers = [col if isinstance(col, basestring) else col.key for col in cols]
    data = {
            "headers": list(headers),
            "data": [ list(row) for row in data],
            "source": table.info(),
            "subs": subs
    }
    return flask.jsonify(data)

def parse_method_and_val(cond):
    if cond.startswith("^"):
        return "startswith", cond[1:], False
    elif cond.startswith("~^"):
        return "startswith", cond[2:], True
    elif cond.endswith("$"):
        return "endswith", cond[:-1], False
    elif cond.endswith("~$"):
        return "endswith", cond[:-2], True
    else:
        return "like", cond, False

def where_filters(table, where_str):
    if not where_str:
        return []
    filts = []

    wheres = where_str.split(",")
    for where in wheres:
        colname, cond = where.split(":")
        col = getattr(table, colname)
        method, value, negate = parse_method_and_val(cond)
        expr = getattr(col, method)(value)
        if negate:
            expr = ~expr
        filts.append(expr)
    return filts

def sumlevel_filtering(table, api_obj):
    shows_and_levels = api_obj.shows_and_levels
    filters = []
    for col, level in shows_and_levels.items():
        args = (table, "{}_filter".format(col))
        if hasattr(*args):
            func = getattr(*args)
            filters.append(func(level))

    # raise Exception(filters)
    return filters

def process_value_filters(table, vars_and_vals):
    filts = []
    for var, val in vars_and_vals.items():
        if consts.OR in val:
            filt = getattr(table, var).in_(val.split(consts.OR))
        else:
            filt = getattr(table, var) == val
        filts.append(filt)
    return filts

def query(table, api_obj):
    vars_and_vals = api_obj.vars_and_vals
    shows_and_levels = api_obj.shows_and_levels
    values = api_obj.values

    filters = process_value_filters(table, vars_and_vals)
    filters += where_filters(table, api_obj.where)
    filters += sumlevel_filtering(table, api_obj)

    if values:
        pk = [col for col in table.__table__.columns if col.primary_key]
        cols = pk + values
    else:
        cols = get_columns(table)

    needs_show_filter = any([v != consts.ALL for v in shows_and_levels.values()])

    if needs_show_filter and hasattr(table, "gen_show_level_filters"):
        filters += table.gen_show_level_filters(shows_and_levels)

    qry = table.query.with_entities(*cols).filter(*filters)
    if api_obj.order:
        sort = "desc" if api_obj.sort == "desc" else "asc"
        qry = qry.order_by("{} {}".format(api_obj.order, sort))
    if api_obj.limit:
        qry = qry.limit(api_obj.limit)

    data = qry.all()
    return simple_format(table, cols, data, api_obj.subs)
