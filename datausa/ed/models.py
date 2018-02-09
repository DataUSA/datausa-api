from datausa.database import db
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from datausa.attrs.consts import ALL
from datausa.attrs.models import UniversityCrosswalk, Geo
from sqlalchemy.orm import column_property
from datausa.attrs import consts


class GeoId(object):
    LEVELS = [consts.NATION, consts.STATE, consts.COUNTY, consts.MSA, consts.ALL]

    @declared_attr
    def geo(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {consts.GEO: GeoId.LEVELS}

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {consts.NATION: "010", consts.STATE: "040",
                     consts.COUNTY: "050", consts.MSA: "310"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)


class BaseEd(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "ed"}
    supported_levels = {"year": [ALL]}
    source_title = 'Official Cohort Default Rates for Schools'
    source_link = 'https://www2.ed.gov/offices/OSFAP/defaultmanagement/cdr.html'
    source_org = 'Department of Education'

    default_rate = db.Column(db.Float)
    num_defaults = db.Column(db.Integer)
    num_borrowers = db.Column(db.Integer)


class UniversityCols(object):
    @declared_attr
    def opeid(cls):
        return db.Column(db.String(), primary_key=True)

    @declared_attr
    def university(cls):
        return column_property(UniversityCrosswalk.university)

    @classmethod
    def crosswalk_join(cls, qry):
        cond = UniversityCrosswalk.opeid6 == cls.opeid
        return qry.join(UniversityCrosswalk, cond)


class DefaultsYu(BaseEd, UniversityCols):
    __tablename__ = "yu_defaults"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    rate_type = db.Column(db.String())
    default_rate = db.Column(db.Float)
    num_defaults = db.Column(db.Integer)
    num_borrowers = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "year": [ALL],
            "university": [ALL],
            "opeid": [ALL],
        }


class DefaultsYg(BaseEd, GeoId):
    __tablename__ = "yg_defaults"
    median_moe = 1.1

    year = db.Column(db.Integer(), primary_key=True)
    rate_type = db.Column(db.String())
    default_rate = db.Column(db.Float)
    num_defaults = db.Column(db.Integer)
    num_borrowers = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "year": [ALL],
            "geo": GeoId.LEVELS
        }


class DefaultsYur(BaseEd, UniversityCols):
    __tablename__ = "yur_defaults"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    rate_type = db.Column(db.String(), primary_key=True)
    default_rate = db.Column(db.Float)
    num_defaults = db.Column(db.Integer)
    num_borrowers = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "year": [ALL],
            "university": [ALL],
            "opeid": [ALL],
            "rate_type": [ALL]
        }


class DefaultsYure(BaseEd, UniversityCols):
    __tablename__ = "yure_defaults"
    median_moe = 3

    year = db.Column(db.Integer(), primary_key=True)
    rate_type = db.Column(db.String(), primary_key=True)
    ethnic_code = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "year": [ALL],
            "university": [ALL],
            "opeid": [ALL],
            "rate_type": [ALL],
            "ethnic_code": [ALL],
        }
