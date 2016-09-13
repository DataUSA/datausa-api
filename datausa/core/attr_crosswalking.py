'''Attribute crosswalker for join API'''
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, func

from datausa.bls.models import BlsCrosswalk, GrowthILookup, SocCrosswalk
from datausa.attrs.models import GeoCrosswalker

def geo_crosswalk_join(tbl1, tbl2, col):
    my_joins = []
    gc_alias = aliased(GeoCrosswalker)
    j1 = [
        gc_alias, or_(gc_alias.geo_a == tbl1.geo,
                      gc_alias.geo_b == tbl1.geo)
    ]
    j1 = [j1, {"full": False, "isouter": False}]
    my_joins.append(j1)

    j2_cond = or_(
        and_(gc_alias.geo_a == tbl1.geo, gc_alias.geo_b == tbl2.geo),
        and_(gc_alias.geo_b == tbl1.geo, gc_alias.geo_a == tbl2.geo)
    )
    j2 = [tbl2, j2_cond]
    j2 = [j2, {"full": False, "isouter": False}]
    my_joins.append(j2)

    return my_joins

def naics_crosswalk_join(tbl1, tbl2, col, already_joined):
    my_joins = []
    bls_table = None
    pums_table = None

    if tbl1.get_schema_name() == "bls":
        bls_table = tbl1
        pums_table = tbl2
    if tbl2.get_schema_name() == "bls":
        bls_table = tbl2
        pums_table = tbl1

    cond1 = BlsCrosswalk.pums_naics == pums_table.naics if tbl1 is pums_table else BlsCrosswalk.bls_naics == bls_table.naics

    if not BlsCrosswalk.full_name() in already_joined:
        j1 = [[BlsCrosswalk, cond1], {"full": False, "isouter": False}]
        my_joins.append(j1)
        already_joined[BlsCrosswalk.full_name()] = True
    j2_cond = and_(BlsCrosswalk.pums_naics == pums_table.naics,
                    BlsCrosswalk.bls_naics == bls_table.naics)
    j2 = [tbl2, j2_cond]
    j2 = [j2, {"full": False, "isouter": False}]
    my_joins.append(j2)
    return my_joins

def soc_crosswalk_join(tbl1, tbl2, col):
    my_joins = []
    cond1 = True
    pums_table = None
    bls_table = None

    if tbl1.get_schema_name() == "bls":
        bls_table = tbl1
    elif tbl2.get_schema_name() == "bls":
        bls_table = tbl2
    if tbl1.get_schema_name().startswith("pums"):
        pums_table = tbl1
    elif tbl2.get_schema_name().startswith("pums"):
        pums_table = tbl2

    if pums_table and bls_table:
        AliasedSocCrosswalk = aliased(SocCrosswalk)
        cond1 = AliasedSocCrosswalk.pums_soc == pums_table.soc if tbl1 is pums_table else AliasedSocCrosswalk.bls_soc == bls_table.soc
        j1 = [[AliasedSocCrosswalk, cond1], {"full": False, "isouter": False}]
        my_joins.append(j1)
        j2_cond = and_(AliasedSocCrosswalk.pums_soc == pums_table.soc,
                        AliasedSocCrosswalk.bls_soc == bls_table.soc)
        j2 = [[tbl2, j2_cond], {"full": False, "isouter": False}]
        my_joins.append(j2)
    else:
        onet_table = tbl1 if tbl1.get_schema_name() == 'onet' else tbl2
        other_table = pums_table or bls_table
        j2_cond = or_(onet_table.soc == other_table.soc,
                     onet_table.soc == func.left(other_table.soc, 2) + '0000',
                     onet_table.soc == func.left(other_table.soc, 3) + '000',
                     onet_table.soc == func.left(other_table.soc, 3) + '100',
                     onet_table.soc == func.left(other_table.soc, 5) + '0')
        my_joins.append([[tbl2, j2_cond], {}])
    return my_joins

def cip_crosswalk_join(tbl1, tbl2, col):
    if tbl1.get_schema_name().startswith('pums'):
        pums_table = tbl1
    elif tbl2.get_schema_name().startswith('pums'):
        pums_table = tbl2
    if tbl1.get_schema_name() == 'ipeds':
        deeper_table = tbl1
    elif tbl2.get_schema_name() == 'ipeds':
        deeper_table = tbl2
    if tbl1.get_schema_name() == 'onet':
        deeper_table = tbl1
    elif tbl1.get_schema_name() == 'onet':
        deeper_table = tbl2
    direct_join = getattr(pums_table, col) == func.left(getattr(deeper_table, col), 2)

    my_joins = [[[tbl2, direct_join], {"full": False, "isouter": False}]]
    return my_joins
