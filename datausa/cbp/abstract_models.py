from datausa.database import db
from datausa.attrs import consts
from datausa.attrs.models import Naics, Geo
from sqlalchemy.orm import column_property
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA, ALL

class BaseCbp(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "cbp"}
    source_title = 'County Business Patterns'
    est = db.Column(db.Integer())

    emp = db.Column(db.Integer())
    emp_nf = db.Column(db.String())
    empflag = db.Column(db.String())

    ap = db.Column(db.Float())
    ap_nf = db.Column(db.String())

    n1_4 = db.Column(db.Integer())
    n5_9 = db.Column(db.Integer())
    n20_49 = db.Column(db.Integer())
    n50_99 = db.Column(db.Integer())
    n100_249 = db.Column(db.Integer())
    n250_499 = db.Column(db.Integer())
    n500_999 = db.Column(db.Integer())
    n1000 = db.Column(db.Integer())
    n1000_1 = db.Column(db.Integer())
    n1000_2 = db.Column(db.Integer())
    n1000_3 = db.Column(db.Integer())
    n1000_4 = db.Column(db.Integer())

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {NATION: "010", STATE: "040", MSA: "310", COUNTY: "050"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)
