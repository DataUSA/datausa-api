from datausa.pums.abstract_models import *


class Yg(BasePums, Personal, Year, GeoId):
    __tablename__ = "yg"
    median_moe = 1
    supported_levels = {
        GEO_ID: [NATION, STATE, PUMA]
    }

class Ygd(BasePums, Personal, Year, GeoId, DegreeId):
    __tablename__ = "ygd"
    median_moe = 2
