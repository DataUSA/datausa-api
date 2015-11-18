import flask
import sqlalchemy
from flask import Response

from datausa.core import get_columns
from datausa.core.table_manager import TableManager, table_name
from datausa.attrs import consts
from datausa.attrs.views import attr_map
from sqlalchemy.orm import aliased

def use_attr_names(table, qry, cols):
    new_cols = []
    joins = {}
    for col in cols:
        col_str = col if isinstance(col, basestring) else col.key
        orig_str = col_str
        col_str = "iocode" if "_iocode" in col_str else col_str
        if col_str in attr_map:
            attr_obj = attr_map[col_str]
            if col_str in joins:
                # we need to alias
                attr_alias = aliased(attr_obj)
                joins[orig_str] = [attr_alias, getattr(table, orig_str) == attr_alias.id]
                new_cols.append(attr_alias.name.label(orig_str + "_name"))
            else:
                joins[col_str] = [attr_obj, getattr(table, orig_str) == attr_obj.id]
                new_cols.append(attr_obj.name.label(orig_str + "_name"))
        new_cols.append(col)
    for col_str, j in joins.items():
        qry = qry.join(*j)
    return qry, new_cols


def stream_format(table, cols, qry, api_obj):
    def generate():
        yield ','.join([col if isinstance(col, basestring) else col.key for col in cols]) + '\n'
        for row in qry.all():
            row = ['"{}"'.format(x) if isinstance(x, basestring) else str(x) for x in list(row)]
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')

def simple_format(table, cols, data, api_obj):
    headers = [col if isinstance(col, basestring) else col.key for col in cols]
    data = {
            "headers": list(headers),
            "data": [ list(row) for row in data],
            "source": table.info(),
            "subs": api_obj.subs,
            "logic": [table.info() for table in api_obj.table_list]
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
    elif cond.startswith("!"):
        return "ne", int(cond[1:]), False
    elif cond.startswith(">"):
        return "gt", int(cond[1:]), False
    elif cond.startswith("<"):
        return "lt", int(cond[1:]), False
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
        if method == "ne":
            expr = col != value
        elif method == "gt":
            expr = col > value
        elif method == "lt":
            expr = col < value
        else:
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
        if var == consts.YEAR and val in [consts.LATEST, consts.OLDEST]:
            years = TableManager.table_years[table_name(table)]
            filt = table.year == years[val]
        elif consts.OR in val:
            filt = getattr(table, var).in_(val.split(consts.OR))
        else:
            filt = getattr(table, var) == val
        filts.append(filt)
    return filts

def remove_filters(filters, table, col):
    new_filts = []
    for filt in filters:
        if hasattr(filt, "left") and hasattr(filt, "right"):
            if filt.left.key == col:
                continue
        new_filts.append(filt)
    return new_filts

def handle_join(qry, filters, table, api_obj):
    joins = []
    joined_filt = table.JOINED_FILTER
    for col, level in api_obj.shows_and_levels.items():
        if level != consts.ALL:
            if col in joined_filt:
                if not "triggers" in joined_filt[col]:
                    joins.append(joined_filt[col]["table"])
                    filters.append(joined_filt[col]["column"] == level)
                    filters.append(joined_filt[col]["id"] == getattr(table, col))
                else:
                    triggers = joined_filt[col]["triggers"]
                    for target_lvl, starting in triggers:
                        if col in api_obj.vars_and_vals:
                            if api_obj.vars_and_vals[col].startswith(starting) and level == target_lvl:
                                joins.append(joined_filt[col]["table"])
                                filters = remove_filters(filters, table, col)
                                filters.append(joined_filt[col]["id"] == getattr(table, col))
                                filters.append(joined_filt[col]["column"] == api_obj.vars_and_vals[col])
    qry=qry.join(*joins)
    return qry, filters

def query(table, api_obj, stream=False):
    vars_and_vals = api_obj.vars_and_vals
    shows_and_levels = api_obj.shows_and_levels
    values = api_obj.values
    exclude = api_obj.exclude

    filters = process_value_filters(table, vars_and_vals)
    filters += where_filters(table, api_obj.where)
    filters += sumlevel_filtering(table, api_obj)

    if values:
        pk = [col for col in table.__table__.columns if col.primary_key]
        cols = pk + values
    else:
        cols = get_columns(table)

    if exclude:
        cols = [col for col in cols if col.key not in exclude]

    needs_show_filter = any([v != consts.ALL for v in shows_and_levels.values()])

    if needs_show_filter and hasattr(table, "gen_show_level_filters"):
        filters += table.gen_show_level_filters(shows_and_levels)

    # qry = table.query.with_entities(*cols)
    qry = table.query
    if stream:
        qry, cols = use_attr_names(table, qry, cols)
    qry = qry.with_entities(*cols)

    if hasattr(table, "JOINED_FILTER"):
        qry, filters = handle_join(qry, filters, table, api_obj)

    qry = qry.filter(*filters)

    if api_obj.order:
        sort = "desc" if api_obj.sort == "desc" else "asc"
        qry = qry.order_by("{} {} NULLS LAST".format(api_obj.order, sort))
    if api_obj.limit:
        qry = qry.limit(api_obj.limit)

    if stream:
        return stream_format(table, cols, qry, api_obj)

    data = qry.all()
    return simple_format(table, cols, data, api_obj)
