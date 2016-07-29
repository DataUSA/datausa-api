import flask
import sqlalchemy
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from datausa.core.table_manager import TableManager, table_name

from datausa.util.inmem import splitter
from datausa.attrs import consts
from datausa.acs.abstract_models import db
from datausa.core.api import sumlevel_filtering, parse_method_and_val

def val_crosswalk(table, var, val):
    api_obj = ApiObject(vars_and_vals={var: val})

def multitable_value_filters(tables, api_obj):
    filts = []
    for var, val in api_obj.vars_and_vals.items():
        for table in tables:
            if not hasattr(table, var):
                full_name = table.full_name()
                if var.startswith(full_name):
                    var = var[len(full_name) + 1:]
                    raise Exception(var) # TODO test this
                else:
                    continue
            if var == consts.YEAR and val in [consts.LATEST, consts.OLDEST]:
                years = TableManager.table_years[table_name(table)]
                my_year = years[val]
                filt = table.year == my_year
                api_obj.set_year(my_year)
            else:
                from datausa.core.crosswalker import crosswalk
                from datausa.core.models import ApiObject
                api_obj = crosswalk(table, ApiObject(vars_and_vals={var: val}, limit=None, exclude=None))
                new_vals = splitter(api_obj.vars_and_vals[var])
                filt = getattr(table, var).in_(new_vals)
            filts.append(filt)
    return filts


def parse_entities(tables, api_obj):
    '''Give a list of tables and required variables, resolve the underlying objects'''
    values = api_obj.vars_needed

    # force the primary key columns to be returned to avoid potential confusion
    for table in tables:
        my_missing_pks = [col for col in table.__table__.columns if col.primary_key and col.key not in values]
        values += [pkc.key for pkc in my_missing_pks]

    values = set(values)

    col_objs = []
    for value in values:
        for table in tables:
            if hasattr(table, value):
                # TODO use full name only if value appears in multiple tables
                col_objs.append(getattr(table, value).label("{}.{}".format(table.full_name(), value)))
                # break
    return col_objs

def find_overlap(tbl1, tbl2):
    cols1 = [c.key for c in tbl1.__table__.columns]
    cols2 = [c.key for c in tbl2.__table__.columns]
    myset = set(cols1).intersection(cols2)
    return myset

def _check_change(api_obj, tbl, col, vals_orig, vals_new):
    did_crosswalk = any([a != b for a, b in zip(vals_orig, vals_new)])
    if did_crosswalk:
        tname = tbl.full_name()
        api_obj.record_sub(tbl, col, vals_new)
    return api_obj

def indirect_joins(tbl1, tbl2, col, api_obj):
    # does this column appear in vars and vals?
    cond = False
    filters = []
    if col in api_obj.vars_and_vals:
        vals_orig = splitter(api_obj.vars_and_vals[col])
        from datausa.core.crosswalker import crosswalk
        from datausa.core.models import ApiObject
        api_objs1 = [crosswalk(tbl1, ApiObject(vars_and_vals={col: val}, limit=None, exclude=None)) for val in vals_orig]
        vals1 = [tmp_api_obj.vars_and_vals[col] for tmp_api_obj in api_objs1]
        api_objs2 = [crosswalk(tbl2, ApiObject(vars_and_vals={col: val}, limit=None, exclude=None)) for val in vals_orig]
        vals2 = [tmp_api_obj.vars_and_vals[col] for tmp_api_obj in api_objs2]
        pairs = zip(vals1, vals2)
        is_same = all([a == b for a, b in pairs])

        # logic for warning about subs
        api_obj = _check_change(api_obj, tbl1, col, vals_orig, vals1)
        api_obj = _check_change(api_obj, tbl2, col, vals_orig, vals2)

        if not is_same:
            for a, b in pairs:
                aeqb = and_(getattr(tbl1, col) == a, getattr(tbl2, col) == b)
                cond = or_(cond, aeqb)

        cond = and_(cond, getattr(tbl2, col).in_(vals2))
    return cond, filters


def where_filters(tables, where_str):
    if not where_str:
        return []
    filts = []

    wheres = splitter(where_str)
    for where in wheres:
        for table in tables:
            colname, cond = where.split(":")
            if "." in colname:
                target_table, target_col = colname.rsplit(".", 1)
                if "{}.{}".format(table.full_name(), target_col) != colname:
                    continue
                else:
                    colname = target_col

            cols = None
            is_multi_col = "/" in colname
            if is_multi_col:
                colnames = colname.split("/")
                has_all = all([hasattr(table, c) for c in colnames])
                if not has_all:
                    continue
                cols = [getattr(table, c) for c in colnames]
            else:
                if not hasattr(table, colname):
                    continue
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
                if method == 'like' and "%" not in value:
                    method = '__eq__'
                expr = getattr(col, method)(value)
            if negate:
                expr = ~expr

            filts.append(expr)
    return filts

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
            api_obj.warn("Years do not overlap between {} and {}!".format(tbl1.full_name(), tbl2.full_name()))

        join_clause = True
        for col in overlap:
            if col == 'year' and not yr_overlap:
                continue
            else:
                direct_join = getattr(tbl1, col) == getattr(tbl2, col)
                indirs, filts = indirect_joins(tbl1, tbl2, col, api_obj)
                join_clause = and_(join_clause, or_(indirs, direct_join))

        my_joins.append([tbl2, join_clause])
    return my_joins, filts


def get_column_from_tables(tables, col, return_first=True):
    acc = []
    for table in tables:
        if hasattr(table, col):
            if return_first:
                return getattr(table, col)
            else:
                acc.append(getattr(table, col))
    return acc

def handle_ordering(tables, api_obj):
    sort = "desc" if api_obj.sort == "desc" else "asc"
    if api_obj.order not in TableManager.possible_variables:
        raise DataUSAException("Bad order parameter", api_obj.order)
    my_col = get_column_from_tables(tables, api_obj.order)
    sort_expr = getattr(my_col, sort)()
    return sort_expr.nullslast()

def joinable_query(tables, api_obj, tbl_years):
    cols = parse_entities(tables, api_obj)
    qry = db.session.query(*tables).select_from(tables[0]).with_entities(*cols)

    my_joins, filts = make_joins(tables, api_obj, tbl_years)

    if my_joins:
        for join_info in my_joins:
            qry = qry.join(*join_info)

    filts += multitable_value_filters(tables, api_obj)
    filts += where_filters(tables, api_obj.where)


    for table in tables:
        filts += sumlevel_filtering(table, api_obj)

    # TODO: add option to return names in query
    # TODO: allow sumlevel all to be optional?

    if api_obj.order:
        sort_expr = handle_ordering(tables, api_obj)
        qry = qry.order_by(sort_expr)

    qry = qry.filter(*filts)

    if api_obj.limit:
        qry = qry.limit(api_obj.limit)
    return flask.jsonify(x=list(qry), subs=api_obj.subs, warnings=api_obj.warnings)
