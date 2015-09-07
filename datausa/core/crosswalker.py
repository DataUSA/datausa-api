from datausa.attrs.models import PumsNaicsCrosswalk
from datausa.attrs.consts import OR

naics_map = PumsNaicsCrosswalk.get_mapping()

def crosswalk(table, api_obj):
    registered_crosswalks = [
        {"column": "naics", "schema": "pums_beta", "mapping" : naics_map}
    ]

    for rcrosswalk in registered_crosswalks:
        column = rcrosswalk['column']
        schema = rcrosswalk['schema']
        mapping = rcrosswalk['mapping']

        if column in api_obj.vars_and_vals.keys() and table.__table_args__['schema'] == schema:
            curr_vals = api_obj.vars_and_vals[column].split(OR)
            new_vals = [naics_map[val] if val in naics_map else val for val in curr_vals]
            new_val_str = OR.join(new_vals)
            api_obj.vars_and_vals[column] = new_val_str

    return api_obj
