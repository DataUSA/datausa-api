from datausa.database import db
from datausa.attrs import consts
from datausa.attrs.models import University, Cip, Geo
from sqlalchemy.orm import column_property
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA, ALL

class BaseIpeds(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "ipeds_beta"}
    supported_levels = {}

class Tuition(BaseIpeds):
    __abstract__ = True
    
    oos_tuition = db.Column(db.Integer())
    state_tuition = db.Column(db.Integer())
    district_tuition = db.Column(db.Integer())

    oos_fee = db.Column(db.Integer())
    state_fee = db.Column(db.Integer())
    district_fee = db.Column(db.Integer())

class Grads(BaseIpeds):
    __abstract__ = True
    total = db.Column(db.Integer())
#     total_men =  db.Column(db.Integer())
#     total_women = db.Column(db.Integer())
#     total_native = db.Column(db.Integer())
#     total_native_men = db.Column(db.Integer())
#     total_native_women = db.Column(db.Integer())
#     total_asian = db.Column(db.Integer())
#     total_asian_men = db.Column(db.Integer())
#     total_asian_women = db.Column(db.Integer())
#     total_black = db.Column(db.Integer())
#     total_black_men = db.Column(db.Integer())
#     total_black_women = db.Column(db.Integer())
#     total_hispanic = db.Column(db.Integer())
#     total_hispanic_men = db.Column(db.Integer())
#     total_hispanic_women = db.Column(db.Integer())
#     total_hawaiian = db.Column(db.Integer())
#     total_hawaiian_men = db.Column(db.Integer())
#     total_hawaiian_women = db.Column(db.Integer())
#     total_white = db.Column(db.Integer())
#     total_white_men = db.Column(db.Integer())
#     total_white_women = db.Column(db.Integer())
#     total_multi = db.Column(db.Integer())
#     total_multi_men = db.Column(db.Integer())
#     total_multi_women = db.Column(db.Integer())
#     total_unknown = db.Column(db.Integer())
#     total_unknown_men = db.Column(db.Integer())
#     total_unknown_women = db.Column(db.Integer())
#     total_nonresident = db.Column(db.Integer())
#     total_nonresident_men = db.Column(db.Integer())
#     total_nonresident_women = db.Column(db.Integer())

# class GradsYgdState(BaseIpeds):
#     autoload = True
#     __tablename__ = "grads_ygd_state"
#     year = db.Column(db.String(), primary_key=True)
#     geo_id = db.Column(db.String(), primary_key=True)
#     degree_id = db.Column(db.String(), primary_key=True)

#     supported_levels = {
#         "geo_id" : [consts.STATE]
#     }


# class GradsYucd(BaseGrads):
#     __tablename__ = "grads_yucd"
#     year = db.Column(db.String(), primary_key=True)
#     university_id = db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)
#     course_id = db.Column(db.String(), db.ForeignKey(Course.id), primary_key=True)
#     degree_id = db.Column(db.String(), primary_key=True)
#     course_id_len = db.Column(db.Integer())

#     # geo_id = column_property(select([University.state]).where(University.id == university_id).label('geo_id'))
#     supported_levels = {
#         "geo_id" : [consts.STATE],
#         "university_id" : consts.ALL,
#         "course_id": ["2", "6", consts.ALL]
#     }

#     @classmethod
#     def gen_show_level_filters(cls, shows_and_levels):
#         result = []
#         for col,val in shows_and_levels.items():
#             if val != consts.ALL:
#                 if col == "course_id":
#                     result.append( cls.course_id_len == val )
#         return result

#     def __repr__(self):
#         return '<{}>'.format(self.__class__)

# class Enrollment(BaseIpeds):
#     __tablename__ = "enrollment_yu"
#     year = db.Column(db.String(), primary_key=True)
#     university_id = db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)
    
#     total = db.Column(db.Integer())
#     men =  db.Column(db.Integer())
#     women =  db.Column(db.Integer())
#     black =  db.Column(db.Integer())
#     asian =  db.Column(db.Integer())
#     native =  db.Column(db.Integer())
#     unknown =  db.Column(db.Integer())
    
#     supported_levels = {
#         "university_id": "all"
#     }

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
    @declared_attr
    def cip(cls):
        return db.Column(db.String(), db.ForeignKey(Cip.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"]}

    @classmethod
    def cip_filter(cls, level):
        return func.length(cls.cip) == level
