from datausa.core import get_columns
from datausa.core.registrar import registered_models
from datausa.core.exceptions import DataUSAException
from datausa.core import crosswalker
from datausa.attrs import consts
from operator import attrgetter
from sqlalchemy.sql import func
from datausa import cache


@cache.memoize()
def tbl_years():
    years = {}
    for tbl in registered_models:
        tbl_name = "{}.{}".format(tbl.__table_args__["schema"],
                                  tbl.__tablename__)
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


class TableManager(object):
    possible_variables = [col.key for t in registered_models
                          for col in get_columns(t)]
    table_years = tbl_years()

    @classmethod
    def sort_tables(cls, tables):
        pass

    @classmethod
    def table_can_show(cls, table, api_obj):
        shows_and_levels = api_obj.shows_and_levels
        supported_levels = table.get_supported_levels()
        for show_col, show_level in shows_and_levels.items():
            if show_col not in supported_levels:
                print show_col, table.supported_levels, "Supported Levels"
                return False
            else:
                if show_level not in supported_levels[show_col]:
                    return False

        if api_obj.force and table.__tablename__ != api_obj.force:
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
