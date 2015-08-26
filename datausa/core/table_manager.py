from datausa.core import get_columns
from datausa.core.registrar import registered_models
from datausa.core.exceptions import DataUSAException

class TableManager(object):
    possible_variables = [col.key for t in registered_models for col in get_columns(t)]

    @classmethod
    def sort_tables(cls, tables):
        pass

    @classmethod
    def table_can_show(cls, table, shows_and_levels):
        supported_levels = table.get_supported_levels()
        for show_col, show_level in shows_and_levels.items():
            if not show_col in supported_levels:
                print supported_levels
                print show_col, table.supported_levels, "SL"
                return False
            else:
                print supported_levels[show_col]
                if not show_level in supported_levels[show_col]:
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
    def find_table(cls, vars_needed, shows_and_levels):
        table_list = cls.all_tables(vars_needed, shows_and_levels)
        # TODO refine ordering strategy
        return table_list[0]

    @classmethod
    def all_tables(cls, vars_needed, shows_and_levels):
        candidates = []
        for table in registered_models:
            if TableManager.table_has_cols(table, vars_needed):
                if TableManager.table_can_show(table, shows_and_levels):
                    candidates.append(table)
        if not candidates:
            raise DataUSAException("No tables can match the specified query.")
        return candidates
