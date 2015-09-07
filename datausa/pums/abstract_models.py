from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
from datausa.core.exceptions import DataUSAException

from datausa.database import db
from datausa.attrs import consts
from datausa.core.models import BaseModel
from datausa.attrs.models import *
from datausa.attrs.consts import NATION, STATE, PUMA, ALL, GEO_ID


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
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)

class CipId(object):
    @declared_attr
    def cip(cls):
        return db.Column(db.String(), db.ForeignKey(Cip.id), primary_key=True)

class DegreeId(object):
    @declared_attr
    def degree(cls):
        return db.Column(db.String(), db.ForeignKey(PumsDegree.id), primary_key=True)

class NaicsId(object):
    LEVELS = ["0", "1", "2", "all"]
    naics_level = db.Column(db.Integer())

    @declared_attr
    def naics(cls):
        return db.Column(db.String(), db.ForeignKey(PumsNaics.id), primary_key=True)

    @classmethod
    def naics_filter(cls, level):
        if level == consts.ALL:
            return True
        return cls.naics_level == level

class SocId(object):
    LEVELS = ["0", "1", "2", "3", "all"]
    soc_level = db.Column(db.Integer())

    @declared_attr
    def soc(cls):
        return db.Column(db.String(), db.ForeignKey(PumsSoc.id), primary_key=True)

    @classmethod
    def soc_filter(cls, level):
        if level == consts.ALL:
            return True
        return cls.soc_level == level

class RaceId(object):
    @declared_attr
    def race(cls):
        return db.Column(db.String(), db.ForeignKey(PumsRace.id), primary_key=True)

class SexId(object):
    @declared_attr
    def sex(cls):
        return db.Column(db.String(), db.ForeignKey(PumsSex.id), primary_key=True)

class BirthplaceId(object):
    @declared_attr
    def birthplace(cls):
        return db.Column(db.String(), db.ForeignKey(PumsBirthplace.id), primary_key=True)
