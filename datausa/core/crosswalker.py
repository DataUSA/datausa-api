from datausa.attrs.models import PumsNaicsCrosswalk, PumsIoCrosswalk
from datausa.attrs.models import GeoContainment
from datausa.bls.models import BlsCrosswalk, SocCrosswalk
from datausa.attrs.consts import OR
from datausa import cache
from sqlalchemy import or_, and_

def truncate_cip(x, api_obj=None):
     return x[:2]

@cache.memoize()
def pums_to_bls_soc():
    all_objs = SocCrosswalk.query.all()
    return {obj.pums_soc: obj.bls_soc for obj in all_objs}


@cache.memoize()
def pums_to_bls_naics():
    all_objs = BlsCrosswalk.query.all()
    return {obj.pums_naics: obj.bls_naics for obj in all_objs}


@cache.memoize()
def pums_naics_mapping():
    '''Make a dictionary that maps naics codes to PUMS
    NAICS codes'''
    all_objs = PumsNaicsCrosswalk.query.all()
    return {obj.naics: obj.pums_naics for obj in all_objs}


@cache.memoize()
def iocode_mapping():
    '''Make a dictionary that maps naics codes to iocodes'''
    all_objs = PumsIoCrosswalk.query.all()
    return {obj.pums_naics: obj.iocode for obj in all_objs}


def pums_parent_puma(geo_id, api_obj=None):
    '''Some data is only accessible at the PUMA level
    so we crosswalk codes to the nearest PUMA'''
    needs_crosswalk = ["050", "140", "160", "310"]
    prefix = geo_id[:3]
    if prefix in needs_crosswalk:
        puma_cond = and_(GeoContainment.parent_geoid.startswith("7"),
                         GeoContainment.percent_covered >= 90)
        state_cond = and_(GeoContainment.parent_geoid.startswith("040"),
                          GeoContainment.percent_covered >= 10)
        puma_or_state = or_(puma_cond, state_cond)
        filters = [
            and_(GeoContainment.child_geoid == geo_id,
                 puma_or_state)
        ]
        qry = GeoContainment.query.filter(*filters)
        qry = qry.order_by(GeoContainment.percent_covered.desc())
        geos = list(qry.all())
        geo_contain = None
        puma_winner = None
        state_winner = None
        # first find the best fitting puma if it exists
        for geo in geos:
            if geo.parent_geoid[:1] == '7' and (not puma_winner or (geo.percent_covered > puma_winner.percent_covered)):
                puma_winner = geo
        # if there are no pumas to match with, fallback to states
        if not puma_winner:
            for geo in geos:
                if geo.parent_geoid[:3] == '040' and (not state_winner or (geo.percent_covered > state_winner.percent_covered)):
                    state_winner = geo
            geo_contain = state_winner
        else:
            geo_contain = puma_winner

        if geo_contain:
            return geo_contain.parent_geoid
        elif not geo_contain and prefix in ["050", "140", "160"]:
            suffix = geo_id.split("US")[-1][:2]
            return "04000US" + suffix
        elif not geo_contain and prefix == "310":
            raise Exception("Not yet implemented")
    return geo_id

def chr_parents(geo_id, api_obj=None):
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

def industry_iocode_func(naics, api_obj=None):
    my_obj = PumsIoCrosswalk.query.filter(PumsIoCrosswalk.pums_naics == naics).first()
    if hasattr(api_obj, "vars_and_vals"):
        if "industry_level" in api_obj.vars_and_vals and int(api_obj.vars_and_vals["industry_level"]) == 0:
            return my_obj.iocode_parent if my_obj else naics
        else:
            return my_obj.iocode if my_obj else naics
    return naics

def crosswalk(table, api_obj):
    '''Given a table and an API object, determine if any crosswalks need
    to be performed'''
    registered_crosswalks = [
        {"column": "industry_iocode", "schema": "bea", "mapping": industry_iocode_func},
        {"column": "commodity_iocode", "schema": "bea", "mapping": iocode_map},
        {"column": "naics", "schema": "bls", "mapping": pums_to_bls_naics_map},
        {"column": "soc", "schema": "bls", "mapping": pums_to_bls_soc_map},
        # cbp uses same naics coding as bls
        {"column": "naics", "schema": "cbp", "mapping": pums_to_bls_naics_map},
        {"column": "naics", "schema": "pums_beta", "mapping": naics_map},
        {"column": "cip", "schema": "pums_beta", "mapping": truncate_cip},
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
                new_vals = [mapping(val, api_obj=api_obj) for val in curr_vals]
            new_val_str = OR.join(new_vals)
            api_obj.vars_and_vals[column] = new_val_str

            # detect if any changes actually happend
            if curr_vals_str != new_val_str:
                api_obj.subs[column] = new_val_str
    return api_obj

naics_map = pums_naics_mapping()
iocode_map = iocode_mapping()
pums_to_bls_naics_map = pums_to_bls_naics()
pums_to_bls_soc_map = pums_to_bls_soc()