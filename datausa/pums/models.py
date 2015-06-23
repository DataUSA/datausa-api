from datausa.database import db
from sqlalchemy import MetaData
from datausa.attrs import consts

class BasePums(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "pums"}
    avg_age = db.Column(db.Float())
    avg_wage =  db.Column(db.Float())
    num_ppl =  db.Column(db.Integer())

    avg_age_moe = db.Column(db.Float())
    avg_wage_moe =  db.Column(db.Float())
    num_ppl_moe =  db.Column(db.Float())

    def __repr__(self):
        return '<{}>'.format(self.__class__)

class Yeg(BasePums):
    __abstract__ = True
    year = db.Column(db.Integer(), primary_key=True)
    est = db.Column(db.Integer(), primary_key=True)
    geo_id = db.Column(db.String(), primary_key=True)

class StateYeg(Yeg):
    __tablename__ = "state_yeg"
    supported_levels = {
        consts.GEO_ID: [consts.STATE]
    }

class NationYeg(Yeg):
    __tablename__ = "nation_ye"
    supported_levels = {
        consts.GEO_ID: [consts.NATION]
    }