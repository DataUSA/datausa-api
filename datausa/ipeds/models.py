from datausa.ipeds.abstract_models import *
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA, GEO
from datausa.attrs.consts import PLACE, ALL
from sqlalchemy.orm import relationship


class EnrollmentYcu(Enrollment, CipId, UniversityId):
    __tablename__ = "enrollment_ycu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": [ALL]}


class TuitionYgs(Tuition, GeoId, SectorId):
    __tablename__ = "tuition_ygs"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "sector": [ALL]}

class TuitionYc(Tuition, CipId):
    __tablename__ = "tuition_yc"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    oos_tuition_rank = db.Column(db.Integer())
    state_tuition_rank = db.Column(db.Integer())

class TuitionYcu(Tuition, CipId, UniversityId):
    __tablename__ = "tuition_ycu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": [ALL]}

class TuitionYcs(Tuition, CipId, SectorId):
    __tablename__ = "tuition_ycs"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    num_universities = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "sector": [ALL]}

class GradsYc(Grads, CipId):
    __tablename__ = "grads_yc"
    median_moe = 0

    year = db.Column(db.Integer(), primary_key=True)
    grads_rank = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS}

class GradsYcd(Grads, CipId, DegreeId):
    __tablename__ = "grads_ycd"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "degree": [ALL]}

class GradsYcu(Grads, CipId, UniversityId):
    __tablename__ = "grads_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    # parent = relationship('Geo', foreign_keys='GeoContainment.parent_geoid')

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": [ALL],
                GEO: [STATE, COUNTY, MSA, PLACE, ALL]}

class GradsYgc(Grads, GeoId, CipId):
    __tablename__ = "grads_ygc"
    median_moe = 1000
    
    year = db.Column(db.Integer(), primary_key=True)
    grads_total_growth = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, GEO: [NATION, STATE, COUNTY, MSA]}

class GradsPctYcu(GradsPct, CipId, UniversityId):
    __tablename__ = "gradspct_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": [ALL]}


class UnivGeo(BaseIpeds, UniversityId, GeoId):
    __tablename__ = "university_geo"
    median_moe = 0

    @classmethod
    def get_supported_levels(cls):
        return {"university": [ALL],
                GEO: [STATE, COUNTY, MSA, PLACE, ALL]}
