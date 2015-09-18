from datausa.database import db
from datausa.attrs import consts
from datausa.attrs.models import University, Cip, Geo
from datausa.attrs.models import Degree, Sector
from sqlalchemy.orm import column_property
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA, ALL

class BaseIpeds(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "ipeds_beta"}
    supported_levels = {}

class Enrollment(BaseIpeds):
    __abstract__ = True

    enrolled_total = db.Column(db.Integer())
    enrolled_men =  db.Column(db.Integer())
    enrolled_women =  db.Column(db.Integer())
    enrolled_black =  db.Column(db.Integer())
    enrolled_asian =  db.Column(db.Integer())
    enrolled_native =  db.Column(db.Integer())
    enrolled_unknown =  db.Column(db.Integer())

class Tuition(BaseIpeds):
    __abstract__ = True
    
    oos_tuition = db.Column(db.Integer())
    state_tuition = db.Column(db.Integer())
    district_tuition = db.Column(db.Integer())

    oos_fee = db.Column(db.Integer())
    state_fee = db.Column(db.Integer())
    district_fee = db.Column(db.Integer())

class GradsPct(BaseIpeds):
    __abstract__ = True
    pct_total = db.Column(db.Float())
    pct_men = db.Column(db.Float())
    pct_women = db.Column(db.Float())

class Grads(BaseIpeds):
    __abstract__ = True
    grads_total = db.Column(db.Integer())
    grads_men =  db.Column(db.Integer())
    grads_women = db.Column(db.Integer())
    grads_native = db.Column(db.Integer())
    grads_native_men = db.Column(db.Integer())
    grads_native_women = db.Column(db.Integer())
    grads_asian = db.Column(db.Integer())
    grads_asian_men = db.Column(db.Integer())
    grads_asian_women = db.Column(db.Integer())
    grads_black = db.Column(db.Integer())
    grads_black_men = db.Column(db.Integer())
    grads_black_women = db.Column(db.Integer())
    grads_hispanic = db.Column(db.Integer())
    grads_hispanic_men = db.Column(db.Integer())
    grads_hispanic_women = db.Column(db.Integer())
    grads_hawaiian = db.Column(db.Integer())
    grads_hawaiian_men = db.Column(db.Integer())
    grads_hawaiian_women = db.Column(db.Integer())
    grads_white = db.Column(db.Integer())
    grads_white_men = db.Column(db.Integer())
    grads_white_women = db.Column(db.Integer())
    grads_multi = db.Column(db.Integer())
    grads_multi_men = db.Column(db.Integer())
    grads_multi_women = db.Column(db.Integer())
    grads_unknown = db.Column(db.Integer())
    grads_unknown_men = db.Column(db.Integer())
    grads_unknown_women = db.Column(db.Integer())
    grads_nonresident = db.Column(db.Integer())
    grads_nonresident_men = db.Column(db.Integer())
    grads_nonresident_women = db.Column(db.Integer())

class GeoId(object):
    @declared_attr
    def geo_id(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {GEO_ID: [NATION, STATE, PUMA]}

    @classmethod
    def geo_id_filter(cls, level):
        level_map = {NATION: "010", STATE: "040", COUNTY: "050", MSA: "310"}
        level_code = level_map[level]
        return cls.geo_id.startswith(level_code)

class CipId(object):
    LEVELS = ["2", "4", "6", "all"]
    @declared_attr
    def cip(cls):
        return db.Column(db.String(), db.ForeignKey(Cip.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["all", "2", "4", "6"]}

    @classmethod
    def cip_filter(cls, level):
        if level == 'all':
            return True
        return func.length(cls.cip) == level

class UniversityId(object):
    @declared_attr
    def university(cls):
        return db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"university": ["all"]}

class DegreeId(object):
    @declared_attr
    def degree(cls):
        return db.Column(db.String(), db.ForeignKey(Degree.id), primary_key=True)

class SectorId(object):
    @declared_attr
    def sector(cls):
        return db.Column(db.String(), db.ForeignKey(Sector.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"sector": ["all"]}

