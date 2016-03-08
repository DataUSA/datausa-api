import flask
import sqlalchemy
from sqlalchemy import and_
from flask import Response
import json

from datausa.core import get_columns
from datausa.core.table_manager import TableManager, table_name
from datausa.attrs import consts
from datausa.attrs.views import attr_map
from sqlalchemy.orm import aliased
from datausa.util.inmem import splitter
from datausa.core.exceptions import DataUSAException

MAX_LIMIT = 4

def use_attr_names(table, qry, cols):
    new_cols = []
    joins = {}
    for col in cols:
        col_str = col if isinstance(col, basestring) else col.key
        orig_str = col_str
        col_str = "iocode" if "_iocode" in col_str else col_str
        col_str = "pums_degree" if "pums" in table.__table_args__["schema"] and col_str == "degree" else col_str
        if table.__table_args__["schema"] == 'bls' and col_str in ['naics', 'soc']:
            col_str = "bls_{}".format(col_str)
        if col_str in attr_map:
            attr_obj = attr_map[col_str]
            attr_alias = aliased(attr_obj)
            joins[orig_str] = [attr_alias, getattr(table, orig_str) == attr_alias.id]
            new_cols.append(attr_alias.name.label(orig_str + "_name"))

        new_cols.append(col)
    for col_str, j in joins.items():
        qry = qry.join(*j, isouter=True)
    return qry, new_cols


def stream_format(table, cols, qry, api_obj):
    def generate():
        yield ','.join([col if isinstance(col, basestring) else col.key for col in cols]) + '\n'
        for row in qry:
            row = [u'"{}"'.format(x) if isinstance(x, basestring) else str(x) for x in list(row)]
            yield u','.join(row) + u'\n'
    return Response(generate(), mimetype='text/csv')

# def simple_format(table, cols, data, api_obj):
#     ''' Based on https://github.com/al4/orlo/blob/1b3930bae4aa37eb51aed33a97c088e576cb5a99/orlo/route_api.py#L285-L311'''
#     def generate(table):
#         headers = [col if isinstance(col, basestring) else col.key for col in cols]
#         inf = float('inf')
#
#         """
#         A lagging generator to stream JSON so we don't have to hold everything in memory
#         This is a little tricky, as we need to omit the last comma to make valid JSON,
#         thus we use a lagging generator, similar to http://stackoverflow.com/questions/1630320/
#         """
#         yield u'{'
#
#         rows = data.__iter__()
#         try:
#             prev_row = next(rows)  # get first result
#         except StopIteration:
#             # StopIteration here means the length was zero, so yield a valid releases doc and stop
#             yield u'''"data": [],
#                      "headers": {},
#                      "source": {},
#                      "subs": {},
#                      "logic": {}
#             '''.format(json.dumps(list(headers)), json.dumps(table.info(api_obj)), json.dumps(api_obj.subs),
#                        json.dumps([table.info(api_obj) for table in api_obj.table_list])) + u'}'
#             raise StopIteration
#
#         # We have some releases. First, yield the opening json
#         yield u'"data": ['
#
#         # Iterate over the releases
#         for row in rows:
#             yield json.dumps([x if x != inf else None for x in row]) + u', '
#             prev_row = row
#
#         # Now yield the last iteration without comma but with the closing brackets
#         yield json.dumps([x if x != inf else None for x in prev_row]) + u'],'
#         yield u'''"headers": {},
#                  "source": {},
#                  "subs": {},
#                  "logic": {}
#         '''.format(json.dumps(list(headers)), json.dumps(table.info(api_obj)), json.dumps(api_obj.subs),
#                    json.dumps([table.info(api_obj) for table in api_obj.table_list])) + u'}'
#
#     return Response(generate(table), content_type='application/json')

def simple_format(table, cols, data, api_obj):
    headers = [col if isinstance(col, basestring) else col.key for col in cols]
    inf = float('inf')
    data = {
            "headers": list(headers),
            "source": table.info(api_obj),
            "subs": api_obj.subs,
            "logic": [table.info(api_obj) for table in api_obj.table_list],
            "data": [ [x if x != inf else None for x in row] for row in data],
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
    elif cond.startswith("str!"):
        return "ne", str(cond[4:]), False
    elif cond.startswith("!"):
        return "ne", int(cond[1:]), False
    elif cond.startswith(">"):
        return "gt", int(cond[1:]), False
    elif cond.startswith("<"):
        return "lt", int(cond[1:]), False
    elif cond.startswith("R<"):
        return "rt", float(cond[2:]), False
    elif cond.startswith("R>"):
        return "rg", float(cond[2:]), False
    else:
        return "like", cond, False

def where_filters(table, where_str):
    if not where_str:
        return []
    filts = []

    wheres = splitter(where_str)
    for where in wheres:
        colname, cond = where.split(":")
        cols = None
        if "/" in colname:
            cols = [getattr(table, c) for c in colname.split("/")]
        else:
            col = getattr(table, colname)
        method, value, negate = parse_method_and_val(cond)
        if method == "ne":
            expr = col != value
        elif method == "gt":
            expr = col > value
        elif method == "lt":
            expr = col < value
        elif method == "rt":
            expr = and_(cols[1] != 0, cols[0] / cols[1] < value)
        elif method == "rg":
            expr = and_(cols[1] != 0, cols[0] / cols[1] > value)
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

def process_value_filters(table, vars_and_vals, api_obj):
    filts = []
    for var, val in vars_and_vals.items():
        if var == consts.YEAR and val in [consts.LATEST, consts.OLDEST]:
            years = TableManager.table_years[table_name(table)]
            my_year = years[val]
            filt = table.year == my_year
            api_obj.set_year(my_year)
        elif consts.OR in val:
            filt = getattr(table, var).in_(splitter(val))
        else:
            filt = getattr(table, var) == val
        filts.append(filt)
    return filts

def remove_filters(filters, table, col, api_obj):
    new_filts = []
    for filt in filters:
        if hasattr(filt, "left") and hasattr(filt, "right"):
            if filt.left.key == col and isinstance(filt.right.value, basestring):
                if api_obj.vars_and_vals[col] == filt.right.value:
                    continue
        new_filts.append(filt)
    return new_filts


def copy_where_literals(api_obj):
    if hasattr(api_obj, "where") and api_obj.where:
        wheres = splitter(api_obj.where)
        for where in wheres:
            colname, cond = where.split(":")
            if colname not in api_obj.vars_and_vals:
                api_obj.vars_and_vals[colname] = cond
    return api_obj


def handle_join(qry, filters, table, api_obj):
    joins = []
    joined_filt = table.JOINED_FILTER
    # see if we need to copy over which variables are involved
    api_obj = copy_where_literals(api_obj)
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
                                filters = remove_filters(filters, table, col, api_obj)
                                filters.append(joined_filt[col]["id"] == getattr(table, col))
                                filters.append(joined_filt[col]["column"] == api_obj.vars_and_vals[col])
    qry=qry.join(*joins)
    return qry, filters

def query(table, api_obj, stream=False):
    vars_and_vals = api_obj.vars_and_vals
    shows_and_levels = api_obj.shows_and_levels
    values = api_obj.values
    exclude = api_obj.exclude

    filters = process_value_filters(table, vars_and_vals, api_obj)
    filters += where_filters(table, api_obj.where)
    filters += sumlevel_filtering(table, api_obj)

    if values:
        pk = [col for col in table.__table__.columns if col.primary_key and col.key not in values]
        cols = pk + values
    else:
        cols = get_columns(table)

    if exclude:
        cols = [col for col in cols
               if (isinstance(col, basestring) and col not in exclude) or col.key not in exclude]


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
        if api_obj.order not in TableManager.possible_variables:
            if api_obj.order == 'abs(pct_change)':
                pass # allow this
            else:
                raise DataUSAException("Bad order parameter", api_obj.order)
        qry = qry.order_by("{} {} NULLS LAST".format(api_obj.order, sort))
    if api_obj.limit:
        qry = qry.limit(api_obj.limit)

    if stream:
        return stream_format(table, cols, qry, api_obj)

    return simple_format(table, cols, qry, api_obj)
