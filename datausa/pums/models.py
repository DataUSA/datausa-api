from datausa.database import db
from sqlalchemy import MetaData
from datausa.attrs import consts
from datausa.core.models import BaseModel

class BasePums(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "pums"}


    def __repr__(self):
        return '<{}>'.format(self.__class__)

class Personal(object):
    avg_age = db.Column(db.Float())
    avg_wage =  db.Column(db.Float())
    num_ppl =  db.Column(db.Integer())

    avg_age_moe = db.Column(db.Float())
    avg_wage_moe =  db.Column(db.Float())
    num_ppl_moe =  db.Column(db.Float())

# -- Person PUMS tables

class Yeg(BasePums):
    __abstract__ = True
    year = db.Column(db.Integer(), primary_key=True)
    est = db.Column(db.Integer(), primary_key=True)
    geo_id = db.Column(db.String(), primary_key=True)

class PumaYeg(Yeg, Personal):
    __tablename__ = "puma_yeg"
    supported_levels = {
        consts.GEO_ID: [consts.STATE]
    }
    median_moe = 3

class StateYeg(Yeg, Personal):
    __tablename__ = "state_yeg"
    supported_levels = {
        consts.GEO_ID: [consts.STATE]
    }
    median_moe = 2

class NationYeg(Yeg, Personal):
    __tablename__ = "nation_ye"
    supported_levels = {
        consts.GEO_ID: [consts.NATION]
    }
    median_moe = 1

# -- Household PUMS tables
class PTax(object):
    property_tax = db.Column(db.Integer(), primary_key=True)
    num_ppl =  db.Column(db.Integer())
    num_ppl_moe =  db.Column(db.Float())

class NationYegPTax(Yeg, PTax):
    __tablename__ = "nation_yeg_ptax"
    supported_levels = {
        consts.GEO_ID: [consts.NATION]
    }

class StateYegPTax(Yeg, PTax):
    __tablename__ = "state_yeg_ptax"
    supported_levels = {
        consts.GEO_ID: [consts.STATE]
    }

class PumaYegPTax(Yeg, PTax):
    __tablename__ = "puma_yeg_ptax"
    supported_levels = {
        consts.GEO_ID: [consts.PUMA]
    }
