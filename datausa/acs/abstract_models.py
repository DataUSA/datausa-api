from sqlalchemy.ext.declarative import declared_attr

from datausa.database import db
from datausa.attrs.models import Geo
from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, COUNTY
from datausa.attrs.consts import PUMA, MSA, ALL, GEO, PLACE


class GeoId(object):
    LEVELS = [NATION, STATE, COUNTY, MSA, PLACE, ALL]

    @classmethod
    def get_supported_levels(cls):
        return {GEO: GeoId.LEVELS}

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {NATION: "010", STATE: "040",
                     PUMA: "795", MSA: "310",
                     COUNTY: "050", PLACE: "160"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)

    @declared_attr
    def geo(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)


class BaseAcs5(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "acs"}
    supported_levels = {}
    source_title = 'ACS 5-year Estimate'


class BaseAcs3(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "acs_3year"}
    supported_levels = {}
    source_title = 'ACS 3-year Estimate'
