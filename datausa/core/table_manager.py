import operator

from datausa.core import get_columns
from datausa.core.registrar import registered_models
from datausa.core.exceptions import DataUSAException
from datausa.core import crosswalker
from datausa.attrs import consts
from operator import attrgetter
from sqlalchemy.sql import func
from datausa import cache

from datausa.acs.abstract_models import BaseAcs5, BaseAcs3, BaseAcs1
from datausa.util.big_places import is_big_geo

def table_name(tbl):
    return "{}.{}".format(tbl.__table_args__["schema"],
                          tbl.__tablename__)


@cache.memoize()
def tbl_years():
    years = {}
    for tbl in registered_models:
        tbl_name = table_name(tbl)
        if hasattr(tbl, "year"):
            qry = tbl.query.with_entities(
                func.max(tbl.year).label("max_year"),
                func.min(tbl.year).label("min_year"),
            )
            res = qry.one()
            years[tbl_name] = {consts.LATEST: res.max_year,
                               consts.OLDEST: res.min_year}
        else:
            years[tbl_name] = None
    return years


def table_exists(full_tblname):
    return full_tblname in tbl_years()


@cache.memoize()
def tbl_sizes():
    sizes = {}
    for tbl in registered_models:
        tbl_name = table_name(tbl)
        sizes[tbl_name] = tbl.query.count()
    return sizes


class TableManager(object):
    possible_variables = [col.key for t in registered_models
                          for col in get_columns(t)]
    table_years = tbl_years()
    # table_sizes = tbl_sizes()
    @classmethod
    def schema_selector(cls, api_obj):
        # -- If there is a force to an "acs" table (defaults to 5-year)
        #    determine if we can instead use the acs 1 year estimate
        #    schema.
        has_force =  hasattr(api_obj, "force") and api_obj.force
        if has_force:
            schema, tblname = api_obj.force.split(".")
            if schema == 'acs':
                if api_obj.force_schema:
                    schema = BaseAcs1.schema_name
                    api_obj.force = "{}.{}".format(schema, tblname)
                    api_obj.subs["force"] = schema
                    return api_obj
                else:
                    schema = BaseAcs5.schema_name
                    api_obj.force = "{}.{}".format(schema, tblname)
                    api_obj.subs["force"] = schema
        if has_force and api_obj.vars_and_vals and not api_obj.force.startswith(BaseAcs5.schema_name): # Applied fix 5.9.16
            if schema and schema in [BaseAcs5.schema_name, BaseAcs3.schema_name]:
                gvals = api_obj.vars_and_vals["geo"].split(",")
                nation_state_only = all([v[:3] in ["010", "040"] for v in gvals])
                not_ygi_ygo = all(["ygo" not in tblname, "ygi" not in tblname])
                if schema != BaseAcs1.schema_name and nation_state_only and not_ygi_ygo:
                    new_fullname = "{}.{}".format(BaseAcs1.schema_name, tblname)
                    if new_fullname in cls.table_years:
                        api_obj.force = new_fullname
                        api_obj.subs["force"] = api_obj.force
        return api_obj

    @classmethod
    def table_can_show(cls, table, api_obj):
        shows_and_levels = api_obj.shows_and_levels
        supported_levels = table.get_supported_levels()
        vars_and_vals = api_obj.vars_and_vals
        required_geos = [] if "geo" not in vars_and_vals else vars_and_vals["geo"].split(",")

        if table.get_schema_name().startswith("acs"):
            if api_obj.force_schema and table.schema_name != api_obj.force_schema:
                return False

        if table.__table_args__["schema"] in [BaseAcs5.schema_name, BaseAcs1.schema_name, BaseAcs3.schema_name] and required_geos:
            need_to_support = set([my_geo[:3] for my_geo in required_geos])
            required_levels = [consts.LEVEL_TO_GEO[slvl] for slvl in need_to_support]
            cond_check = [x in supported_levels["geo"] for x in required_levels]
            result = all(cond_check)
            if not result:
                return False

        for show_col, show_level in shows_and_levels.items():
            if show_col not in supported_levels:
                # print show_col, supported_levels, "Supported Levels"
                return False
            else:
                if show_level not in supported_levels[show_col]:
                    return False

        if api_obj.force and table.full_name() != api_obj.force:
            return False


        return True

    @classmethod
    def required_tables(cls, api_obj):
        '''Given a list of X, do Y'''
        vars_needed = api_obj.vars_needed
        if api_obj.order and api_obj.order in cls.possible_variables:
            vars_needed = vars_needed + [api_obj.order]
        universe = set(vars_needed)
        tables_to_use = []
        table_cols = []
        # Make a set of the variables that will be needed to answer the query
        while universe:
            # first find the tables with biggest overlap
            candidates = cls.list_partial_tables(universe, api_obj)
            # raise Exception(candidates)
            top_choices = sorted(candidates.items(), key=operator.itemgetter(1),
                                 reverse=True)
            # take the table with the biggest overlap
            tbl, overlap = top_choices.pop(0)
            # ensure the tables are joinable, for now that means
            # having atleast one column with the same name
            if tables_to_use:
                while not set(table_cols).intersection([str(c.key) for c in get_columns(tbl)]):
                    if top_choices:
                        tbl, overlap = top_choices.pop(0)
                    else:
                        raise DataUSAException("can't join tables!")
            tables_to_use.append(tbl)
            tmp_cols = [str(c.key) for c in get_columns(tbl)]
            table_cols += tmp_cols
            # remove the acquired columns from the universe
            universe = universe - set(tmp_cols)
        return tables_to_use

    @classmethod
    def list_partial_tables(cls, vars_needed, api_obj):
        candidates = {}
        for table in registered_models:
            overlap_size = TableManager.table_has_some_cols(table, vars_needed)
            if overlap_size > 0:
                if TableManager.table_can_show(table, api_obj):
                    # to break ties, we'll use median moe to penalize and subtract
                    # since larger values will be chosen first.
                    penalty = (1 - (1.0 / table.median_moe)) if table.median_moe > 0 else 0
                    candidates[table] = overlap_size - penalty
        if not candidates:
            raise DataUSAException("No tables2 can match the specified query.")
        return candidates

    @classmethod
    def table_has_some_cols(cls, table, vars_needed):
        '''
        Go through the list of required variables find tables that have
        atleast 2 variables (if more than one variable is needed). The reason atleast
        2 are required is allow a join to occur (one for the value, one to potentially join).
        '''
        table_cols = get_columns(table)
        cols = set([col.key for col in table_cols])
        # min_overlap = 2 if len(vars_needed) > 1 else 1
        intersection = set(vars_needed).intersection(cols)

        if intersection:
            return len(intersection)
        return None # TODO review this

    @classmethod
    def table_has_cols(cls, table, vars_needed):
        table_cols = get_columns(table)
        cols = set([col.key for col in table_cols])
        return set(vars_needed).issubset(cols)

    @classmethod
    def select_best(cls, table_list, api_obj):
        # Ordering is sorted in all_tables
        return table_list[0]

    @classmethod
    def all_tables(cls, api_obj):
        vars_needed = api_obj.vars_needed
        candidates = []
        for table in registered_models:
            if api_obj.order and api_obj.order in cls.possible_variables:
                vars_needed = vars_needed + [api_obj.order]
            if TableManager.table_has_cols(table, vars_needed):
                if TableManager.table_can_show(table, api_obj):
                    candidates.append(table)
        candidates = sorted(candidates, key=attrgetter('median_moe'))
        if not candidates:
            raise DataUSAException("No tables can match the specified query.")
        return candidates

    @classmethod
    def multi_crosswalk(cls, tables, api_obj):
        for tbl in tables:
            api_obj = crosswalker.crosswalk(tbl, api_obj)
        return api_obj

    @classmethod
    def crosswalk(cls, table, api_obj):
        return crosswalker.crosswalk(table, api_obj)

    @classmethod
    def force_1yr_for_big_places(cls, api_obj):
        # -- if we are trying to look at tracts, that data is only available
        # -- at 5yr resolution.
        if api_obj.shows_and_levels and "geo" in api_obj.shows_and_levels and api_obj.shows_and_levels["geo"] == "tract":
            return api_obj
        if api_obj.vars_and_vals and "geo" in api_obj.vars_and_vals:
            cond_a = "med_earnings" in api_obj.values or "med_earnings_moe" in api_obj.values
            cond_b = "acs_ind" in api_obj.shows_and_levels
            cond_c = any(["languge" in api_obj.shows_and_levels, "language" in api_obj.values, "num_speakers" in api_obj.values, "num_speakers_moe" in api_obj.values, "num_speakers_rca" in api_obj.values])
            if (cond_a and cond_b) or cond_c:
                return api_obj
            geos = api_obj.vars_and_vals["geo"].split(consts.OR)
            if not api_obj.force or api_obj.force.startswith("acs."):
                can_use_1yr = all([is_big_geo(geo) for geo in geos])
                if can_use_1yr:
                    api_obj.force_schema = BaseAcs1.schema_name
        return api_obj
