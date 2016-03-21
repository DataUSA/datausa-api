from datausa import cache
from sqlalchemy import or_, and_
from sqlalchemy import distinct
from datausa.attrs.consts import POP_THRESHOLD
from datausa.acs.automap_models import Acs1_Yg

@cache.memoize()
def get_big_geos():
    conds = [
        Acs1_Yg.geo.startswith("010"),
        Acs1_Yg.geo.startswith("040"),
        Acs1_Yg.geo.startswith("050"),
        Acs1_Yg.geo.startswith("160"),
        Acs1_Yg.geo.startswith("310"),
    ]
    cond = and_(or_(*conds), Acs1_Yg.pop > POP_THRESHOLD)
    geos = Acs1_Yg.query.with_entities(distinct(Acs1_Yg.geo)).filter(cond).all()
    return set([g for g, in geos]) # faster lookup with set

def is_big_geo(geo_id):
    # for sufficiently large places, we can also rely on 1-year estimate
    return geo_id in big_geos

big_geos = get_big_geos()
