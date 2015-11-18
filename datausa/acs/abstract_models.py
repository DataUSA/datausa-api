from sqlalchemy.ext.declarative import declared_attr

from datausa.database import db
from datausa.attrs.models import Geo, AcsOcc, AcsInd, GeoContainment
from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, COUNTY
from datausa.attrs.consts import PUMA, MSA, ALL, GEO
from datausa.attrs.consts import PLACE, TRACT
from sqlalchemy.sql import func

class AcsIndId(object):
    LEVELS = ["0", "1", "2", ALL]

    @classmethod
    def acs_ind_filter(cls, level):
        if level == ALL:
            return True
        else:
            target = (int(level) * 2) + 2
            return func.length(cls.acs_ind) == target

    @classmethod
    def get_supported_levels(cls):
        return {"acs_ind": AcsIndId.LEVELS}

    @declared_attr
    def acs_ind(cls):
        return db.Column(db.String(), db.ForeignKey(AcsInd.id),
                         primary_key=True)

class AcsOccId(object):
    LEVELS = ["0", "1", "2", "3", "4", ALL]

    @classmethod
    def get_supported_levels(cls):
        return {"acs_occ": AcsOccId.LEVELS}

    @declared_attr
    def acs_occ(cls):
        return db.Column(db.String(), db.ForeignKey(AcsOcc.id),
                         primary_key=True)

    @classmethod
    def acs_occ_filter(cls, level):
        if level == ALL:
            return True
        else:
            target = (int(level) * 2) + 2
            return func.length(cls.acs_occ) == target


class GeoId(object):
    LEVELS = [NATION, STATE, COUNTY, MSA, PUMA, PLACE, TRACT, ALL]
    JOINED_FILTER = {"geo": {
                            "triggers": [("tract", "160"), ("county", "310")],
                            "table": GeoContainment.parent,
                            "column": GeoContainment.parent_geoid,
                            "id": GeoContainment.child_geoid,
    }}
    @classmethod
    def get_supported_levels(cls):
        return {GEO: GeoId.LEVELS}

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {NATION: "010", STATE: "040",
                     PUMA: "795", MSA: "310",
                     COUNTY: "050", PLACE: "160", TRACT: "140"}
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
    source_link = 'http://www.census.gov/programs-surveys/acs/'


class BaseAcs3(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "acs_3year"}
    supported_levels = {}
    source_title = 'ACS 3-year Estimate'
    source_link = 'http://www.census.gov/programs-surveys/acs/'
