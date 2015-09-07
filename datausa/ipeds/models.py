from datausa.ipeds.abstract_models import *
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA

class EnrollmentYcu(Enrollment, CipId, UniversityId):
    __tablename__ = "enrollment_ycu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer())

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
    grads_total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "university": ["all"]}

class TuitionYcs(Tuition, CipId, SectorId):
    __tablename__ = "tuition_ycs"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    num_universities = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "sector": ["all"]}

class GradsYc(Grads, CipId):
    __tablename__ = "grads_yc"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_rank = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"]}

class GradsYcd(Grads, CipId, DegreeId):
    __tablename__ = "grads_ycd"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "degree": ["all"]}

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
    grads_total_growth = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "geo_id": [NATION, STATE, COUNTY, MSA]}

class GradsPctYcu(GradsPct, CipId, UniversityId):
    __tablename__ = "gradspct_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"], "university": ["all"]}