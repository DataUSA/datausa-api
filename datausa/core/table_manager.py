from datausa.core import get_columns
from datausa.core.registrar import registered_models
from datausa.core.exceptions import DataUSAException
from datausa.core import crosswalker
from datausa.attrs import consts
from operator import attrgetter
from sqlalchemy.sql import func
from datausa import cache


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
        # -- If there is a force to an "acs" table (5-year)
        #    determine if we can instead use the acs_1year
        #    schema.
        if hasattr(api_obj, "force") and api_obj.force and api_obj.vars_and_vals:
            schema, tblname = api_obj.force.split(".")
            if schema and schema in ["acs", "acs_3year"]:
                gvals = api_obj.vars_and_vals["geo"].split(",")
                nation_state_only = all([v[:3] in ["010", "040"] for v in gvals])
                not_ygi_ygo = all(["ygo" not in tblname, "ygi" not in tblname])
                if schema != "acs_1year" and nation_state_only and not_ygi_ygo:
                    new_fullname = "acs_1year.{}".format(tblname)
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
        if required_geos and supported_levels and "geo" in supported_levels:
            need_to_support = set([my_geo[:3] for my_geo in required_geos])
            required_levels = [consts.LEVEL_TO_GEO[slvl] for slvl in need_to_support]
            cond_check = [x in supported_levels["geo"] for x in required_levels]
            return all(cond_check)

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
            if TableManager.table_has_cols(table, vars_needed):
                if TableManager.table_can_show(table, api_obj):
                    candidates.append(table)
        candidates = sorted(candidates, key=attrgetter('median_moe'))
        if not candidates:
            raise DataUSAException("No tables can match the specified query.")
        return candidates

    @classmethod
    def crosswalk(cls, table, api_obj):
        return crosswalker.crosswalk(table, api_obj)
