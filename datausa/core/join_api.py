import flask
import sqlalchemy
import itertools
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from datausa.core.table_manager import TableManager, table_name

from datausa.util.inmem import splitter
from datausa.attrs import consts
from datausa.acs.abstract_models import db
from datausa.core.api import parse_method_and_val
from datausa.core.crosswalker import crosswalk
from datausa.core.models import ApiObject
from datausa.attrs.views import attr_map


def use_attr_names(qry, cols):
    new_cols = []
    joins = {}
    for col in cols:
        full_name = str(col)
        full_table_name, var_name = full_name.rsplit(".", 1)
        # TODO THIS LOGIC:
        # col_str = "pums_degree" if "pums" in table.__table_args__["schema"] and col_str == "degree" else col_str
        if full_name.startswith("pums") and full_name.endswith(".degree"):
            var_name = "pums_degree"
        elif full_name.startswith("bls") and (full_name.endswith(".naics") or full_name.endswith(".soc")):
            var_name = "bls_{}".format(var_name)
        # if table.__table_args__["schema"] == 'bls' and col_str in ['naics', 'soc']:
            # col_str = "bls_{}".format(col_str)

        if var_name in attr_map:
            attr_obj = attr_map[var_name]
            attr_alias = aliased(attr_obj)
            joins[full_name] = [attr_alias, col == attr_alias.id]
            new_cols.append(attr_alias.name.label(full_name + "_name"))

        new_cols.append(col)
    for col_str, j in joins.items():
        qry = qry.join(*j, isouter=True)
    return qry, new_cols

def sumlevel_filtering2(table, api_obj):
    shows_and_levels = api_obj.shows_and_levels
    filters = []
    for col, level in shows_and_levels.items():
        args = (table, "{}_filter".format(col))
        if hasattr(*args):
            func = getattr(*args)
            expr = func(level)
            if api_obj.auto_crosswalk:
                filters.append(expr)
            else:
                filters.append(or_(expr, getattr(table, col) == None))
    return filters

def val_crosswalk(table, var, val):
    api_obj = ApiObject(vars_and_vals={var: val})

def find_table(tables, colname):
    target_table, colname = colname.rsplit(".", 1)
    lookup = {tbl.full_name(): tbl for tbl in tables}
    return colname, [lookup[target_table]]


def multitable_value_filters(tables, api_obj):
    filts = []

    for colname, val in api_obj.vars_and_vals.items():
        related_tables = tables_by_col(tables, colname)
        if not api_obj.auto_crosswalk:
            filts += gen_combos(related_tables, colname, val)
        else:
            for table in related_tables:
                if colname == consts.YEAR and val in [consts.LATEST, consts.OLDEST]:
                    years = TableManager.table_years[table_name(table)]
                    my_year = years[val]
                    filt = or_(table.year == my_year, table.year == None)
                    api_obj.set_year(my_year)
                else:
                    api_obj_tmp = crosswalk(table, ApiObject(vars_and_vals={colname: val}, limit=None, exclude=None))
                    new_vals = splitter(api_obj_tmp.vars_and_vals[colname])
                    mycol = getattr(table, colname)
                    filt = mycol.in_(new_vals)
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
        api_obj.record_sub(tbl, col, vals_orig, vals_new)
    return api_obj

def indirect_joins(tbl1, tbl2, col, api_obj):
    # does this column appear in vars and vals?
    cond = False
    filters = []
    if col in api_obj.vars_and_vals and api_obj.auto_crosswalk:
        vals_orig = splitter(api_obj.vars_and_vals[col])
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

def gen_combos(tables, colname, val):
    combos = []
    relevant_tables = tables_by_col(tables, colname)

    possible_combos = list(itertools.combinations(relevant_tables, 2))
    if len(possible_combos) > 0:
        for table1, table2 in possible_combos:
            val1 = splitter(val)
            val2 = splitter(val)
            if colname == consts.YEAR and val in [consts.LATEST, consts.OLDEST]:
                years1 = TableManager.table_years[table1.full_name()]
                years2 = TableManager.table_years[table2.full_name()]
                val1 = [years1[val]]
                val2 = [years2[val]]
            cond1 = and_(getattr(table1, colname).in_(val1), getattr(table2, colname).in_(val2))
            cond2 = and_(getattr(table1, colname).in_(val1), getattr(table2, colname) == None)
            cond3 = and_(getattr(table1, colname) == None, getattr(table2, colname).in_(val2))
            combos.append(or_(cond1, cond2, cond3))
    elif not len(possible_combos) and len(relevant_tables) == 1:
        # if we're just referencing a single table
        safe_colname = colname.rsplit(".", 1)[-1]
        combos.append(getattr(relevant_tables[0], safe_colname) == val)
    return combos

def where_filters2(tables, api_obj):
    where_str = api_obj.where
    if not where_str:
        return []
    wheres = splitter(where_str)
    filts = []

    for where in wheres:
        colname, val = where.split(":")
        filts += gen_combos(tables, colname, val)
    return filts

def where_filters(tables, api_obj):
    where_str = api_obj.where
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
                if api_obj.auto_crosswalk:
                    # raise Exception("yoohoo")
                    join_clause = and_(join_clause, or_(indirs, direct_join))
                else:
                    join_clause = and_(join_clause, direct_join)


        my_joins.append([tbl2, join_clause])
    return my_joins, filts


def tables_by_col(tables, col, return_first=False):
    acc = []
    for table in tables:
        if hasattr(table, col):
            if return_first:
                return table
            else:
                acc.append(table)
        elif "." in col:
            table_name, colname = col.rsplit(".", 1)
            if table_name == table.full_name() and hasattr(table, colname):
                if return_first:
                    return table
                else:
                    acc.append(table)

    return acc

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

def complex_filters(tables, api_obj):
    '''The complex filters are provided to the api in the format:
        <variable name>.<associated variable to filter>=<value>
        e.g.
        grads_total.year=2013
    '''
    filts = []
    for key, value in api_obj.complex_filters.items():
        target_var, filt_col = key.split(".")
        cols = get_column_from_tables(tables, target_var, False)
        for col in cols:
            # if hasattr(table, filt_col):
            table = col.class_
            filts.append(getattr(table, filt_col) == value)
    return filts

def joinable_query(tables, api_obj, tbl_years):
    cols = parse_entities(tables, api_obj)
    qry = db.session.query(*tables)
    qry = qry.select_from(tables[0])

    my_joins, filts = make_joins(tables, api_obj, tbl_years)

    if my_joins:
        for join_info in my_joins:
            qry = qry.join(*join_info, full=True, isouter=True)

    if api_obj.display_names:
        qry, cols = use_attr_names(qry, cols)

    qry = qry.with_entities(*cols)

    filts += multitable_value_filters(tables, api_obj)
    filts += complex_filters(tables, api_obj)

    if api_obj.auto_crosswalk:
        filts += where_filters(tables, api_obj)
    else:
        filts += where_filters2(tables, api_obj)

    for table in tables:
        filts += sumlevel_filtering2(table, api_obj)

    # TODO: add option to return names in query
    # TODO: allow sumlevel all to be optional?

    if api_obj.order:
        sort_expr = handle_ordering(tables, api_obj)
        qry = qry.order_by(sort_expr)

    qry = qry.filter(*filts)

    if api_obj.limit:
        qry = qry.limit(api_obj.limit)
    return flask.jsonify(data=list(qry), subs=api_obj.subs, warnings=api_obj.warnings)
