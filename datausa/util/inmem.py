from datausa import cache
from datausa.ipeds.models import GradsYgc


@cache.memoize()
def ipeds_place_map():
    qry = GradsYgc.query.with_entities(GradsYgc.geo.distinct()).all()
    return {item: True for item, in qry}

# print ipeds_place_map()