from datausa.attrs.models import PumsNaicsCrosswalk, IoCodeCrosswalk
from datausa.attrs.models import GeoContainment
from datausa.attrs.consts import OR
from datausa import cache
from sqlalchemy import or_


@cache.memoize()
def pums_naics_mapping():
    '''Make a dictionary that maps naics codes to PUMS
    NAICS codes'''
    all_objs = PumsNaicsCrosswalk.query.all()
    return {obj.naics: obj.pums_naics for obj in all_objs}


@cache.memoize()
def iocode_mapping():
    '''Make a dictionary that maps naics codes to iocodes'''
    all_objs = IoCodeCrosswalk.query.all()
    return {obj.naics: obj.iocode for obj in all_objs}


def pums_parent_puma(geo_id):
    '''Some data is only accessible at the PUMA level
    so we crosswalk codes to the nearest PUMA'''
    needs_crosswalk = ["050", "140", "160", "310"]
    prefix = geo_id[:3]
    if prefix in needs_crosswalk:
        filters = [
            GeoContainment.child_geoid == geo_id,
            GeoContainment.parent_geoid.startswith("7")
        ]
        qry = GeoContainment.query.filter(*filters)
        qry = qry.order_by(GeoContainment.percent_covered.desc())
        geo_contain = qry.first()
        if geo_contain:
            return geo_contain.parent_geoid
        elif not geo_contain and prefix in ["050", "140", "160"]:
            suffix = geo_id.split("US")[-1][:2]
            return "04000US" + suffix
        elif not geo_contain and prefix == "310":
            raise Exception("Not yet implemented")
    return geo_id

def chr_parents(geo_id):
    '''CHR data'''
    needs_crosswalk = ["160", "310", "795"]
    prefix = geo_id[:3]
    if prefix in needs_crosswalk:
        filters = [
            GeoContainment.child_geoid == geo_id,
            or_(GeoContainment.parent_geoid.startswith("040"),
                GeoContainment.parent_geoid.startswith("050"))
        ]
        qry = GeoContainment.query.filter(*filters)
        qry = qry.order_by(GeoContainment.percent_covered.desc())
        geo_contain = qry.first()
        if geo_contain:
            return geo_contain.parent_geoid
    return geo_id

def crosswalk(table, api_obj):
    '''Given a table and an API object, determine if any crosswalks need
    to be performed'''
    registered_crosswalks = [
        {"column": "industry_iocode", "schema": "bea", "mapping": iocode_map},
        {"column": "naics", "schema": "pums_beta", "mapping": naics_map},
        {"column": "cip", "schema": "pums_beta", "mapping": lambda x: x[:2]},
        {"column": "geo", "schema": "pums_beta", "mapping": pums_parent_puma},
        {"column": "geo", "schema": "chr", "mapping": chr_parents}

    ]

    for rcrosswalk in registered_crosswalks:
        column = rcrosswalk['column']
        schema = rcrosswalk['schema']
        mapping = rcrosswalk['mapping']

        if column in api_obj.vars_and_vals.keys() and table.__table_args__['schema'] == schema:
            curr_vals_str = api_obj.vars_and_vals[column]
            curr_vals = curr_vals_str.split(OR)
            if isinstance(mapping, dict):
                new_vals = [mapping[val] if val in mapping else val for val in curr_vals]
            else:
                new_vals = [mapping(val) for val in curr_vals]
            new_val_str = OR.join(new_vals)
            api_obj.vars_and_vals[column] = new_val_str

            # detect if any changes actually happend
            if curr_vals_str != new_val_str:
                api_obj.subs[column] = new_val_str
    return api_obj

naics_map = pums_naics_mapping()
iocode_map = iocode_mapping()
