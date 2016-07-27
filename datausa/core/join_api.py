import flask
import sqlalchemy
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from datausa.core.table_manager import TableManager, table_name

from datausa.util.inmem import splitter
from datausa.attrs import consts
from datausa.acs.abstract_models import db

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
            else:
                vals = splitter(val)
                from datausa.core.crosswalker import crosswalk
                from datausa.core.models import ApiObject
                api_objs = [crosswalk(table, ApiObject(vars_and_vals={var: val}, limit=None, exclude=None)) for val in vals]
                vals = [api_obj.vars_and_vals[var] for api_obj in api_objs]
                filt = getattr(table, var).in_(vals)
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


            # raise Exception("here!", vals1, col)
        # elif t2_no_crosswalk:
            # filters.append(
                # getattr(tbl2, col).in_(vals2)
            # )
            # raise Exception("here!", vals2, col)

        if not is_same:
            for a, b in pairs:
                aeqb = and_(getattr(tbl1, col) == a, getattr(tbl2, col) == b)
                cond = or_(cond, aeqb)
                # getattr(tbl1)

        cond = and_(cond, getattr(tbl2, col).in_(vals2))
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
                # indirs,filts = indirect_joins(tbl1, tbl2, col, api_obj)
                # join_clause = and_(join_clause, direct_join)
                join_clause = and_(join_clause, direct_join)

        my_joins.append([tbl2, join_clause])
    return my_joins, filts

def join_query(tables, api_obj, tbl_years):
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
