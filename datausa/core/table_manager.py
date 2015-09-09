from datausa.core import get_columns
from datausa.core.registrar import registered_models
from datausa.core.exceptions import DataUSAException
from operator import attrgetter

class TableManager(object):
    possible_variables = [col.key for t in registered_models for col in get_columns(t)]

    @classmethod
    def sort_tables(cls, tables):
        pass

    @classmethod
    def table_can_show(cls, table, api_obj):
        shows_and_levels = api_obj.shows_and_levels
        supported_levels = table.get_supported_levels()
        for show_col, show_level in shows_and_levels.items():
            if not show_col in supported_levels:
                print show_col, table.supported_levels, "Supported Levels"
                return False
            else:
                if not show_level in supported_levels[show_col]:
                    return False

        if api_obj.force and table.__tablename__ != api_obj.force:
            return False

        return True
    
    @classmethod
    def table_has_cols(cls, table, vars_needed):
        table_cols = get_columns(table)
        cols = set([col.key for col in table_cols])
        # if table.__tablename__ == 'ygd':
            # raise Exception(vars_needed, cols, set(vars_needed).issubset(cols))
        return set(vars_needed).issubset(cols)

    @classmethod
    def find_table(cls, api_obj):
        table_list = cls.all_tables(api_obj)
        # Ordering is sorted in all_tables
        return table_list[0]

    @classmethod
    def all_tables(cls, api_obj):
        vars_needed = api_obj.vars_needed
        shows_and_levels = api_obj.shows_and_levels
        candidates = []
        for table in registered_models:
            if TableManager.table_has_cols(table, vars_needed):
                if TableManager.table_can_show(table, api_obj):
                    candidates.append(table)
        candidates = sorted(candidates, key=attrgetter('median_moe'))
        if not candidates:
            raise DataUSAException("No tables can match the specified query.")
        return candidates
