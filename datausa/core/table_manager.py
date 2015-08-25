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
        for show_col, show_level in shows_and_levels.items():
            if not show_col in table.supported_levels:
                return False
            else:
                print table.supported_levels[show_col]
                if not show_level in table.supported_levels[show_col]:
                    return False
        return True
    
    @classmethod
    def table_has_cols(cls, table, vars_needed):
        cols = set([col.key for col in get_columns(table)])
        # if table.__tablename__ == 'grads_yucd':
            # raise Exception("t")
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
