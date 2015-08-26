from datausa.database import db
from sqlalchemy import MetaData
from datausa.core.models import BaseModel
from datausa.attrs.models import Geo, PumsDegree
from datausa.attrs.consts import NATION, STATE, PUMA, ALL, GEO_ID
from datausa.core.exceptions import DataUSAException
from sqlalchemy.ext.declarative import declared_attr

def geo_sumlevel_filter(table, show_colname, sumlevel):
    sumlevel_codes = {NATION: "010", STATE: "040", PUMA: "795"}
    if not sumlevel in sumlevel_codes:
        raise DataUSAException("Invalid sumlevel", sumlevel)
    start_code = sumlevel_codes[sumlevel]
    return table.geo_id.startswith(start_code)

class BasePums(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "pums_beta"}

    @classmethod
    def gen_show_level_filters(cls, shows_and_levels):
        result = []
        for show_colname, sumlevel in shows_and_levels.items():
            if sumlevel != ALL:
                if show_colname == "geo_id":
                    filt = geo_sumlevel_filter(cls, show_colname, sumlevel)
                    result.append(filt)

        return result

    def __repr__(self):
        return '<{}>'.format(self.__class__)

class Personal(object):
    avg_age = db.Column(db.Float())
    avg_wage =  db.Column(db.Float())
    avg_hrs =  db.Column(db.Float())
    num_ppl =  db.Column(db.Integer())

    avg_age_moe = db.Column(db.Float())
    avg_wage_moe =  db.Column(db.Float())
    avg_hrs_moe = db.Column(db.Float())

    num_ppl_moe =  db.Column(db.Float())


class Year(object):
    @declared_attr
    def year(cls):
        return db.Column(db.Integer(), primary_key=True)

class GeoId(object):

    @classmethod
    def get_supported_levels(cls):
        return {GEO_ID: [NATION, STATE, PUMA]}

    @declared_attr
    def geo_id(cls):
        return db.Column(db.String(6), db.ForeignKey(Geo.id), primary_key=True)

class DegreeId(object):
    @declared_attr
    def degree(cls):
        return db.Column(db.String(6), db.ForeignKey(PumsDegree.id), primary_key=True)
