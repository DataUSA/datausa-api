import flask
import sqlalchemy
from sqlalchemy import and_, or_
from sqlalchemy.sql import text
from flask import Response
import simplejson

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

def simple_format(table, cols, data, api_obj):
    ''' Based on https://github.com/al4/orlo/blob/1b3930bae4aa37eb51aed33a97c088e576cb5a99/orlo/route_api.py#L285-L311'''
    def generate(table):
        headers = [col if isinstance(col, basestring) else col.key for col in cols]
        inf = float('inf')

        """
        A lagging generator to stream JSON so we don't have to hold everything in memory
        This is a little tricky, as we need to omit the last comma to make valid JSON,
        thus we use a lagging generator, similar to http://stackoverflow.com/questions/1630320/
        """
        yield u'{'

        rows = data.__iter__()
        try:
            prev_row = next(rows)  # get first result
        except StopIteration:
            # StopIteration here means the length was zero, so yield a valid releases doc and stop
            yield u'''"data": [],
                     "headers": {},
                     "source": {},
                     "subs": {},
                     "logic": {}
            '''.format(simplejson.dumps(list(headers)), simplejson.dumps(table.info(api_obj)), simplejson.dumps(api_obj.subs),
                       simplejson.dumps([table.info(api_obj) for table in api_obj.table_list])) + u'}'
            raise StopIteration

        # We have some releases. First, yield the opening json
        yield u'"data": ['

        # Iterate over the releases
        for row in rows:
            yield simplejson.dumps([x if x != inf else None for x in prev_row]) + u', '
            prev_row = row

        # Now yield the last iteration without comma
        yield simplejson.dumps([x if x != inf else None for x in prev_row])

        yield u'''], "headers": {},
                 "source": {},
                 "subs": {},
                 "logic": {}
        '''.format(simplejson.dumps(list(headers)), simplejson.dumps(table.info(api_obj)), simplejson.dumps(api_obj.subs),
                   simplejson.dumps([table.info(api_obj) for table in api_obj.table_list])) + u'}'

    return Response(generate(table), content_type='application/json')

# def simple_format(table, cols, data, api_obj):
#     headers = [col if isinstance(col, basestring) else col.key for col in cols]
#     inf = float('inf')
#     data = {
#             "headers": list(headers),
#             "source": table.info(api_obj),
#             "subs": api_obj.subs,
#             "logic": [table.info(api_obj) for table in api_obj.table_list],
#             "data": [ [x if x != inf else None for x in row] for row in data],
#     }
#
#     return flask.jsonify(data)

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
        sort_stmt = text("{} {} NULLS LAST".format(api_obj.order, sort))
        qry = qry.order_by(sort_stmt)
    if api_obj.limit:
        qry = qry.limit(api_obj.limit)

    if stream:
        return stream_format(table, cols, qry, api_obj)

    return simple_format(table, cols, qry, api_obj)

###########################
def val_crosswalk(table, var, val):
    api_obj = ApiObject(vars_and_vals={var: val})

def multitable_value_filters(tables, api_obj):
    filts = []
    for var, val in api_obj.vars_and_vals.items():
        for table in tables:
            if not hasattr(table, var): continue
            if var == consts.YEAR and val in [consts.LATEST, consts.OLDEST]:
                years = TableManager.table_years[table_name(table)]
                my_year = years[val]
                filt = table.year == my_year
                api_obj.set_year(my_year)
            # else:
            #     vals = splitter(val)
            #     from datausa.core.crosswalker import crosswalk
            #     from datausa.core.models import ApiObject
            #     api_objs = [crosswalk(table, ApiObject(vars_and_vals={var: val}, limit=None, exclude=None)) for val in vals]
            #     vals = [api_obj.vars_and_vals[var] for api_obj in api_objs]
            #     # check if the vals need crosswalks
            #     # raise Exception(vals)
            #     filt = getattr(table, var).in_(vals)
                filts.append(filt)
    return filts


def parse_entities(tables, api_obj):
    '''Give a list of tables and required variables, resolve the underlying objects'''
    values = set(api_obj.vars_needed)

    col_objs = []
    for value in values:
        for table in tables:
            if hasattr(table, value):
                # TODO use full name only if value appears in multiple tables
                col_objs.append(getattr(table, value).label("{}_{}".format(table.full_name(), value)))
                # break
    return col_objs

def find_overlap(tbl1, tbl2):
    cols1 = [c.key for c in tbl1.__table__.columns]
    cols2 = [c.key for c in tbl2.__table__.columns]
    myset = set(cols1).intersection(cols2)
    return myset

def indirect_joins(tbl1, tbl2, col, api_obj):
    # does this column appear in vars and vals?
    cond = False
    filters = []
    if col in api_obj.vars_and_vals:
        vals_orig = splitter(api_obj.vars_and_vals[col])
        from datausa.core.crosswalker import crosswalk
        from datausa.core.models import ApiObject
        api_objs1 = [crosswalk(tbl1, ApiObject(vars_and_vals={col: val}, limit=None, exclude=None)) for val in vals_orig]
        vals1 = [api_obj.vars_and_vals[col] for api_obj in api_objs1]
        api_objs2 = [crosswalk(tbl2, ApiObject(vars_and_vals={col: val}, limit=None, exclude=None)) for val in vals_orig]
        vals2 = [api_obj.vars_and_vals[col] for api_obj in api_objs2]
        pairs = zip(vals1, vals2)
        is_same = all([a == b for a, b in pairs])

        t1_no_crosswalk = all([a == b for a, b in zip(vals_orig, vals1)])
        t2_no_crosswalk = all([a == b for a, b in zip(vals_orig, vals2)])

        if t1_no_crosswalk:
            filters.append(
                getattr(tbl1, col).in_(vals1)
            )
        elif t2_no_crosswalk:
            filters.append(
                getattr(tbl2, col).in_(vals2)
            )


        if not is_same:
            for a, b in pairs:
                aeqb = and_(getattr(tbl1, col) == a, getattr(tbl2, col) == b)
                cond = or_(cond, aeqb)
                # getattr(tbl1)
    return cond, filters

def make_joins(tables, api_obj, tbl_years):
    my_joins = []
    filts = []
    from sqlalchemy.sql.expression import join
    for idx, tbl1 in enumerate(tables[:-1]):
        tbl2 = tables[idx + 1]
        overlap = find_overlap(tbl1, tbl2)

        # check if years overlap
        years1 = sorted([int(v) for v in tbl_years[tbl1.full_name()].values()])
        years1[-1] += 1
        years2 = sorted([int(v) for v in tbl_years[tbl2.full_name()].values()])
        years2[-1] += 1
        years1range = range(*years1)
        years2range = range(*years2)
        yr_overlap = set(years1range).intersection(years2range)

        if not yr_overlap:
            api_obj.subs["warning"] = "years do not overlap!"

        join_clause = True
        for col in overlap:
            if col == 'year' and not yr_overlap:
                continue
            else:
                direct_join = getattr(tbl1, col) == getattr(tbl2, col)
                # at this point what we need to be able to do is to either do a
                # direct join, (where boston=boston) OR an indirect join
                # e.g. (so boston=massachusetts) because we need a crosswalk
                indirs,filts = indirect_joins(tbl1, tbl2, col, api_obj)
                # join_clause = and_(join_clause, direct_join)
                join_clause = and_(join_clause, or_(indirs, direct_join))
                # if indirs is not None:
                    # join_clause = or_(join_clause, indirs)
        my_joins.append([tbl1, join_clause])
    return my_joins, filts

def join_query(tables, api_obj, tbl_years):
    from datausa.acs.abstract_models import db
    cols = parse_entities(tables, api_obj)

    qry = db.session.query(*tables).with_entities(*cols)
    my_joins, filts = make_joins(tables, api_obj, tbl_years)

    if my_joins:
        for join_info in my_joins:
            qry = qry.join(*join_info)

    filts += multitable_value_filters(tables, api_obj)

    #16000US2507000
    # for table in tables:
        # filters += sumlevel_filtering(table, api_obj)

    qry = qry.filter(*filts)

    if api_obj.limit:
        qry = qry.limit(api_obj.limit)
    # raise Exception(qry)
    return flask.jsonify(x=list(qry))
