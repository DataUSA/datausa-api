from datausa.attrs.models import PumsNaicsCrosswalk, IoCodeCrosswalk
from datausa.attrs.consts import OR
from datausa import cache

@cache.memoize()
def pums_naics_mapping():
    '''Make a dictionary that maps naics codes to PUMS
    NAICS codes'''
    all_objs = PumsNaicsCrosswalk.query.all()
    return {obj.naics : obj.pums_naics for obj in all_objs}

@cache.memoize()
def iocode_mapping():
    '''Make a dictionary that maps naics codes to iocodes'''
    all_objs = IoCodeCrosswalk.query.all()
    return {obj.naics : obj.iocode for obj in all_objs}

def crosswalk(table, api_obj):
    '''Given a table and an API object, determine if any crosswalks need
    to be performed'''
    registered_crosswalks = [
        {"column": "industry_iocode", "schema": "bea", "mapping" : iocode_map},
        {"column": "naics", "schema": "pums_beta", "mapping" : naics_map},
        {"column": "cip", "schema": "pums_beta", "mapping" : lambda x: x[:2]}
    ]

    for rcrosswalk in registered_crosswalks:
        column = rcrosswalk['column']
        schema = rcrosswalk['schema']
        mapping = rcrosswalk['mapping']

        if column in api_obj.vars_and_vals.keys() and table.__table_args__['schema'] == schema:
            curr_vals = api_obj.vars_and_vals[column].split(OR)
            if isinstance(mapping, dict):
                new_vals = [mapping[val] if val in mapping else val for val in curr_vals]
            else:
                new_vals = [mapping(val) for val in curr_vals]
            new_val_str = OR.join(new_vals)
            api_obj.vars_and_vals[column] = new_val_str
            api_obj.subs[column] = new_val_str
    return api_obj

naics_map = pums_naics_mapping()
iocode_map = iocode_mapping()
