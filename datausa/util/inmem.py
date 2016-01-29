from datausa import cache
from datausa.ipeds.models import GradsYgc
from datausa.onet.models import SkillBySoc, SkillByCip
import re

def splitter(x):
    return re.split(",(?! )", x)

@cache.memoize()
def ipeds_place_map():
    qry = GradsYgc.query.with_entities(GradsYgc.geo.distinct()).all()
    return {item: True for item, in qry}


@cache.memoize()
def onet_socs():
    qry = SkillBySoc.query.with_entities(SkillBySoc.soc.distinct()).all()
    return {item: True for item, in qry}


@cache.memoize()
def onet_cips():
    qry = SkillByCip.query.with_entities(SkillByCip.cip.distinct()).all()
    return {item: True for item, in qry}
