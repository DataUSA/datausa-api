from datausa.ipeds.abstract_models import *
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA

class EnrollmentYcu(Enrollment, CipId, UniversityId):
    __tablename__ = "enrollment_ycu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    total_grads = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "university": ["all"]}

class TuitionYc(Tuition, CipId):
    __tablename__ = "tuition_yc"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)

class TuitionYcu(Tuition, CipId, UniversityId):
    __tablename__ = "tuition_ycu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "university": ["all"]}

class GradsYcu(Grads, CipId, UniversityId):
    __tablename__ = "grads_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "university": ["all"]}

class GradsYgc(Grads, GeoId, CipId):
    __tablename__ = "grads_ygc"
    median_moe = 2
    
    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "geo_id": [NATION, STATE, COUNTY, MSA]}