'''naics crosswalker'''
from datausa.bls.models import BlsCrosswalk, GrowthILookup
from sqlalchemy import and_, or_

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
