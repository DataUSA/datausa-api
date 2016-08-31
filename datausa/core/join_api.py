import itertools
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import join

from datausa.core.table_manager import TableManager, table_name

from datausa.util.inmem import splitter
from datausa.attrs import consts
from datausa.acs.abstract_models import db
from datausa.core.api import parse_method_and_val
from datausa.core.crosswalker import crosswalk
from datausa.core.models import ApiObject
from datausa.attrs.views import attr_map
from datausa.attrs.models import GeoContainment
from datausa.core.streaming import stream_qry, stream_qry_csv
from datausa.core.attr_crosswalking import naics_crosswalk_join, soc_crosswalk_join
from datausa.core.attr_crosswalking import cip_crosswalk_join

def use_attr_names(qry, cols):
    '''This method will return a query object with outer joins to include
    description names for all columns which have attribute data'''
    new_cols = []
    joins = {}
    for col in cols:
        full_name = str(col)
        full_table_name, var_name = full_name.rsplit(".", 1)
        if full_name.startswith("pums") and full_name.endswith(".degree"):
            var_name = "pums_degree"
        elif full_name.startswith("bls") and (full_name.endswith(".naics") or full_name.endswith(".soc")):
            var_name = "bls_{}".format(var_name)

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
    '''This method provides the logic to handle sumlevel filtering.
    If auto-crosswalk mode is true the conditions will be simple, otherwise
    NULLs will be allowed so that NULL rows can be retained for the result sent back to
    the users'''
    shows_and_levels = api_obj.shows_and_levels
    filters = []
    for col, level in shows_and_levels.items():
        args = (table, "{}_filter".format(col))
        if hasattr(*args):
            if api_obj.auto_crosswalk:
                raise Exception(col, level)
            func = getattr(*args)
            expr = func(level)
            if api_obj.auto_crosswalk:
                filters.append(expr)
            else:
                filters.append(or_(expr, getattr(table, col) == None))
    return filters

def find_table(tables, colname):
    '''Given a list of tables and the name of a fully qualified column
    (e.g. chr.yg.geo) return the shortened column name (e.g geo)
    and the table to which it belongs
    '''
    target_table, colname = colname.rsplit(".", 1)
    lookup = {tbl.full_name(): tbl for tbl in tables}
    return colname, [lookup[target_table]]

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
                col_objs.append(getattr(table, value).label("{}.{}".format(table.full_name(), value)))
                # break
    return col_objs

def find_overlap(tbl1, tbl2):
    '''Given two table objects, determine the set of intersecting columns by
    column name'''
    cols1 = [c.key for c in tbl1.__table__.columns]
    cols2 = [c.key for c in tbl2.__table__.columns]
    myset = set(cols1).intersection(cols2)
    return myset

def _check_change(api_obj, tbl, col, vals_orig, vals_new):
    '''Check if any subsitutions occured by examining whether original values (pre-crosswalk)
    equal new values (post-crosswalk)'''
    did_crosswalk = any([a != b for a, b in zip(vals_orig, vals_new)])
    if did_crosswalk:
        tname = tbl.full_name()
        api_obj.record_sub(tbl, col, vals_orig, vals_new)
    return api_obj

def has_same_levels(tbl1, tbl2, col):
    levels1 = tbl1.get_supported_levels()[col]
    levels2 = tbl2.get_supported_levels()[col]
    return set(levels1) == set(levels2)

def geo_crosswalk_join(tbl1, tbl2, col):
    my_joins = []
    tbl1_mode, tbl2_mode = table_depths(tbl1, tbl2, col)

    gc_alias = aliased(GeoContainment)
    j1 = [
        gc_alias, getattr(gc_alias, tbl1_mode) == tbl1.geo
    ]
    j1 = [j1, {"full": False, "isouter": False}]
    my_joins.append(j1)

    j2_cond = or_(and_(
                    getattr(gc_alias, tbl1_mode) == tbl1.geo,
                    getattr(gc_alias, tbl2_mode) == tbl2.geo),
                  tbl1.geo == tbl2.geo)
    j2 = [tbl2, j2_cond]
    j2 = [j2, {"full": False, "isouter": False}]
    my_joins.append(j2)

    return my_joins

def indirect_joins(tbl1, tbl2, col, api_obj):
    '''When joining tables in auto-crosswalk mode, a simple a.x=b.x will not work
    since, if values are crosswalked, the values may be different for each table.
    The varying values based on crosswalking are taken into account during the join process.'''
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


def make_filter(table, col, cond):
    cols = None

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
    where_str = api_obj.where
    if not where_str:
        return []
    filts = []

    wheres = splitter(where_str)
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
                filt = make_filter(table, filt_col, cond)
                filts.append(filt)
    return filts

def table_depths(tbl1, tbl2, col):
    if tbl1.get_schema_name() == 'chr' and tbl2.get_schema_name().startswith('pums'):
        return "child_geoid", "parent_geoid"
    else:
        # raise Exception("Not yet implemented!!!", tbl1, tbl2)
        size1 = len(tbl1.get_supported_levels()[col])
        size2 = len(tbl2.get_supported_levels()[col])
        return ["child_geoid", "parent_geoid"] if size1 > size2 else ["parent_geoid", "child_geoid"]

def make_joins(tables, api_obj, tbl_years):
    my_joins = []
    filts = []
    already_naics_joined = {}
    for idx, tbl1 in enumerate(tables[:-1]):
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
            api_obj.warn("Years do not overlap between {} and {}!".format(tbl1.full_name(), tbl2.full_name()))

        join_clause = True
        # TODO test direct joins

        # for col in overlap:
        #     if col == 'year' and not yr_overlap:
        #         continue
        #     else:
        #         direct_join = getattr(tbl1, col) == getattr(tbl2, col)
        #         if api_obj.auto_crosswalk:
        #             # raise Exception("yoohoo")
        #             indirs, filts = indirect_joins(tbl1, tbl2, col, api_obj)
        #             join_clause = and_(join_clause, or_(indirs, direct_join))
        #         else:
        #             join_clause = and_(join_clause, direct_join)

        for col in overlap:
            if col == 'year': # or has_same_levels(tbl1, tbl2, col):
                continue
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

        if join_clause != True:
            my_joins.append([[tbl2, direct_join], {}])
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

def build_filter(table, filt_col, value):
    method, value, negate = parse_method_and_val(value)
    col = getattr(table, filt_col)
    if method == 'like' and "%" not in value:
        if consts.OR in value:
            value = splitter(value)
            method = "in_"
        else:
            method = '__eq__'

    if hasattr(col, method):
        expr = getattr(col, method)(value)
    else:
        raise DataUSAException("bad parameter", value)
    return expr



def joinable_query(tables, api_obj, tbl_years, csv_format=False):
    cols = parse_entities(tables, api_obj)
    tables = sorted(tables, key=lambda x: x.full_name())
    qry = db.session.query(*tables)
    qry = qry.select_from(tables[0])

    my_joins, filts = make_joins(tables, api_obj, tbl_years)

    if my_joins:
        for join_info, kwargs in my_joins:
            qry = qry.join(*join_info, **kwargs)

    if api_obj.display_names:
        qry, cols = use_attr_names(qry, cols)


    qry = qry.with_entities(*cols)

    filts += multitable_value_filters(tables, api_obj)
    filts += where_filters(tables, api_obj)

    # for table in tables:
        # filts += sumlevel_filtering2(table, api_obj)

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
