'''
Implementation of logic for joining variables across tables
'''
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
from datausa.core.streaming import stream_qry, stream_qry_csv
from datausa.core.attr_crosswalking import naics_crosswalk_join, soc_crosswalk_join
from datausa.core.attr_crosswalking import cip_crosswalk_join, geo_crosswalk_join
from datausa.core.exceptions import DataUSAException
from datausa.core import get_columns

def use_attr_names(qry, cols):
    '''This method will return a query object with outer joins to include
    description names for all columns which have attribute data'''
    new_cols = []
    joins = {}
    for col in cols:
        full_name = str(col)
        _, var_name = full_name.rsplit(".", 1)
        if full_name.startswith("pums") and full_name.endswith(".degree"):
            var_name = "pums_degree"
        elif full_name.startswith("bls") and (full_name.endswith(".naics")
                                              or full_name.endswith(".soc")):
            var_name = "bls_{}".format(var_name)

        if var_name in attr_map:
            attr_obj = attr_map[var_name]
            attr_alias = aliased(attr_obj)
            joins[full_name] = [attr_alias, col == attr_alias.id]
            new_cols.append(attr_alias.name.label(full_name + "_name"))

        new_cols.append(col)
    for my_joins in joins.values():
        qry = qry.join(*my_joins, isouter=True)
    return qry, new_cols

def sumlevel_filtering2(table, api_obj):
    '''This method provides the logic to handle sumlevel filtering.
    If auto-crosswalk mode is true the conditions will be simple, otherwise
    NULLs will be allowed so that NULL rows can be retained for the result sent back to
    the users'''
    shows_and_levels = api_obj.shows_and_levels
    filters = []
    for col, level in shows_and_levels.items():
        args = (table, "{}_filter".format(col))
        if hasattr(*args):
            func = getattr(*args)
            expr = func(level)
            filters.append(or_(expr, getattr(table, col) == None))
    return filters

def multitable_value_filters(tables, api_obj):
    '''This method examines the values pased in query args (e.g. year=2014 or
    geo=04000US25), and applies the logic depending on the crosswalk mode.
    If the auto-crosswalk is not enabled, special logic (gen_combos) is required
    to preserve null values so the user will see that no value is available.
    Otherwise, if auto-crosswalk is enabled, treat each filter as an AND conjunction.
    Return the list of filters to be applied.
    '''
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
                    api_obj_tmp = crosswalk(table,
                                            ApiObject(vars_and_vals={colname: val},
                                                      limit=None, exclude=None))
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
        my_missing_pks = [col for col in table.__table__.columns
                          if col.primary_key and col.key not in values]
        values += [pkc.key for pkc in my_missing_pks]

    values = set(values)

    col_objs = []
    for value in values:
        for table in tables:
            if hasattr(table, value):
                val_label = "{}.{}".format(table.full_name(), value)
                col_objs.append(getattr(table, value).label(val_label))
    return col_objs

def find_overlap(tbl1, tbl2):
    '''Given two table objects, determine the set of intersecting columns by
    column name'''
    cols1 = [col.key for col in get_columns(tbl1)]
    cols2 = [col.key for col in get_columns(tbl2)]
    myset = set(cols1).intersection(cols2)
    return myset

def has_same_levels(tbl1, tbl2, col):
    '''Check if two tables have the same exact sumlevels for the given column'''
    levels1 = tbl1.get_supported_levels()[col]
    levels2 = tbl2.get_supported_levels()[col]
    return set(levels1) == set(levels2)

def gen_combos(tables, colname, val):
    '''Generate the required logical condition combinations to optionally
    join two tables'''
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

def make_filter(col, cond):
    '''Generate SQLAlchemy filter based on string'''
    method, value, negate = parse_method_and_val(cond)
    if method == "ne":
        expr = col != value
    elif method == "gt":
        expr = col > value
    elif method == "lt":
        expr = col < value
    # elif method == "rt":
        # expr = and_(cols[1] != 0, cols[0] / cols[1] < value)
    # elif method == "rg":
        # expr = and_(cols[1] != 0, cols[0] / cols[1] > value)
    else:
        if method == 'like' and "%" not in value:
            method = '__eq__'
        expr = getattr(col, method)(value)
    if negate:
        expr = ~expr

    return expr

def where_filters(tables, api_obj):
    '''Process the where query argument from an API call'''
    if not api_obj.where:
        return []
    filts = []

    wheres = splitter(api_obj.where)
    for where in wheres:
        colname, cond = where.split(":")
        target_var, filt_col = colname.rsplit(".", 1)

        if filt_col == 'sumlevel':
            filt_col = api_obj.shows_and_levels.keys()[0]
            cols = get_column_from_tables(tables, target_var, False)
            table = tables_by_col(tables, target_var, return_first=True)
            args = (table, "{}_filter".format(filt_col))
            if hasattr(*args):
                func = getattr(*args)
                filts.append(func(cond))
        else:
            cols = get_column_from_tables(tables, target_var, False)
            for col in cols:
                table = col.class_
                filt_col = getattr(table, filt_col)
                filt = make_filter(filt_col, cond)
                filts.append(filt)
    return filts

def make_joins(tables, api_obj, tbl_years):
    '''Generate the joins required to combine tables'''
    my_joins = []
    filts = []
    already_naics_joined = {}
    tbl1 = tables[0]
    for idx, _ in enumerate(tables[:-1]):
        tbl2 = tables[idx + 1]
        overlap = find_overlap(tbl1, tbl2)

        # check if years overlap
        if hasattr(tbl1, "year") and hasattr(tbl2, "year"):
            years1 = sorted([int(v) for v in tbl_years[tbl1.full_name()].values()])
            years1[-1] += 1
            years2 = sorted([int(v) for v in tbl_years[tbl2.full_name()].values()])
            years2[-1] += 1
            years1range = range(*years1)
            years2range = range(*years2)
            yr_overlap = set(years1range).intersection(years2range)
        else:
            yr_overlap = False

        if not yr_overlap:
            api_obj.warn("Years do not overlap between {} and {}!".format(
                tbl1.full_name(), tbl2.full_name()))

        join_clause = True

        for col in overlap:
            if col == 'year': # or has_same_levels(tbl1, tbl2, col):
                continue
            if api_obj.auto_crosswalk:
                lvls_are_eq = has_same_levels(tbl1, tbl2, col)
                if col == consts.GEO and not lvls_are_eq:
                    my_joins += geo_crosswalk_join(tbl1, tbl2, col)
                elif col == 'naics' and not lvls_are_eq:
                    my_joins += naics_crosswalk_join(tbl1, tbl2, col, already_naics_joined)
                elif col == 'soc' and not lvls_are_eq:
                    my_joins += soc_crosswalk_join(tbl1, tbl2, col)
                elif col == 'cip' and not lvls_are_eq:
                    my_joins += cip_crosswalk_join(tbl1, tbl2, col)
                else:
                    direct_join = getattr(tbl1, col) == getattr(tbl2, col)
                    join_clause = and_(join_clause, direct_join)
            else:
                direct_join = getattr(tbl1, col) == getattr(tbl2, col)
                join_clause = and_(join_clause, direct_join)

        if join_clause != True:
            join_params = {} if api_obj.auto_crosswalk else {"isouter": True, "full": True}
            my_joins.append([[tbl2, direct_join], join_params])

    return my_joins, filts


def tables_by_col(tables, col, return_first=False):
    '''Return a table or a list of tables that contain the given column'''
    acc = []
    for table in tables:
        if hasattr(table, col):
            if return_first:
                return table
            else:
                acc.append(table)
        elif "." in col:
            my_table_name, colname = col.rsplit(".", 1)
            if my_table_name == table.full_name() and hasattr(table, colname):
                if return_first:
                    return table
                else:
                    acc.append(table)

    return acc

def get_column_from_tables(tables, col, return_first=True):
    '''Given a list of tables return the reference to the column in a
    list of tables'''
    acc = []
    for table in tables:
        if hasattr(table, col):
            if return_first:
                return getattr(table, col)
            else:
                acc.append(getattr(table, col))
    return acc

def handle_ordering(tables, api_obj):
    '''Process sort and order parameters from the API'''
    sort = "desc" if api_obj.sort == "desc" else "asc"
    if api_obj.order not in TableManager.possible_variables:
        raise DataUSAException("Bad order parameter", api_obj.order)
    my_col = get_column_from_tables(tables, api_obj.order)
    sort_expr = getattr(my_col, sort)()
    return sort_expr.nullslast()


def joinable_query(tables, api_obj, tbl_years, csv_format=False):
    '''Entry point from the view for processing join query'''
    cols = parse_entities(tables, api_obj)
    tables = sorted(tables, key=lambda x: x.full_name())
    qry = db.session.query(*tables)
    qry = qry.select_from(tables[0])

    my_joins, filts = make_joins(tables, api_obj, tbl_years)
    for table in tables:
        if hasattr(table, "crosswalk_join"):
            qry = table.crosswalk_join(qry)
    if my_joins:
        for join_info, kwargs in my_joins:
            qry = qry.join(*join_info, **kwargs)

    if api_obj.display_names:
        qry, cols = use_attr_names(qry, cols)


    qry = qry.with_entities(*cols)

    filts += multitable_value_filters(tables, api_obj)
    filts += where_filters(tables, api_obj)

    if not api_obj.auto_crosswalk:
        for table in tables:
            filts += sumlevel_filtering2(table, api_obj)

    if api_obj.order:
        sort_expr = handle_ordering(tables, api_obj)
        qry = qry.order_by(sort_expr)

    qry = qry.filter(*filts)

    if api_obj.limit:
        qry = qry.limit(api_obj.limit)

    if api_obj.offset:
        qry = qry.offset(api_obj.offset)

    if csv_format:
        return stream_qry_csv(cols, qry, api_obj)
    return stream_qry(tables, cols, qry, api_obj)
