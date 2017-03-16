from datausa.database import db
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from datausa.attrs.consts import STATE, COUNTY, ALL
from datausa.attrs.models import Geo, Sctg, ProductCrosswalk
from sqlalchemy.orm import column_property

class BaseFreight(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "freight"}
    supported_levels = {}
    source_title = 'Freight Analysis Framework'
    source_link = 'https://www.rita.dot.gov/bts/sites/rita.dot.gov.bts/files/subject_areas/freight_transportation/faf'
    source_org = 'Bureau of Transportation Statistics'
    tons = db.Column(db.Float)
    millions_of_2012_dollars = db.Column(db.Float)


class Product(object):
    @declared_attr
    def sctg(cls):
        return db.Column(db.String(), db.ForeignKey(Sctg.id), primary_key=True)

    @declared_attr
    def napcs(cls):
        return column_property(ProductCrosswalk.napcs)

    @classmethod
    def crosswalk_join(cls, qry):
        cond = ProductCrosswalk.sctg == cls.sctg
        return qry.join(ProductCrosswalk, cond)

class OriginGeo(object):
    @declared_attr
    def origin_geo(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)

    @classmethod
    def origin_geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {STATE: "040", COUNTY: "050"}
        level_code = level_map[level]
        return cls.origin_geo.startswith(level_code)

class DestGeo(object):
    @declared_attr
    def destination_geo(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)

    @classmethod
    def destination_geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {STATE: "040", COUNTY: "050"}
        level_code = level_map[level]
        return cls.destination_geo.startswith(level_code)


class FAFYodmp(BaseFreight, OriginGeo, DestGeo, Product):
    __tablename__ = "yodmp_faf"
    median_moe = 4
    year = db.Column(db.Integer(), primary_key=True)
    transportation_mode = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "destination_geo": [STATE, COUNTY, ALL],
            "transportation_mode": [ALL],
            "sctg": [ALL],
            "napcs": [ALL]
        }

class FAFYodm(BaseFreight, OriginGeo, DestGeo):
    __tablename__ = "yodm_faf"
    median_moe = 3
    year = db.Column(db.Integer(), primary_key=True)
    transportation_mode = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "destination_geo": [STATE, COUNTY, ALL],
            "transportation_mode": [ALL]
        }

class FAFYod(BaseFreight, OriginGeo, DestGeo):
    __tablename__ = "yod_faf"
    median_moe = 2
    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "destination_geo": [STATE, COUNTY, ALL]
        }


class FAFYodp(BaseFreight, OriginGeo, DestGeo, Product):
    __tablename__ = "yodp_faf"
    median_moe = 3
    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "destination_geo": [STATE, COUNTY, ALL],
            "sctg": [ALL],
            "napcs": [ALL]
        }

class FAFYomp(BaseFreight, OriginGeo, Product):
    __tablename__ = "yomp_faf"
    median_moe = 3
    year = db.Column(db.Integer(), primary_key=True)
    transportation_mode = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "transportation_mode": [ALL],
            "sctg": [ALL],
            "napcs": [ALL]
        }

class FAFYop(BaseFreight, OriginGeo, Product):
    __tablename__ = "yop_faf"
    median_moe = 2
    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "sctg": [ALL],
            "napcs": [ALL]
        }

class FAFYdp(BaseFreight, DestGeo, Product):
    __tablename__ = "ydp_faf"
    median_moe = 2
    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "destination_geo": [STATE, COUNTY, ALL],
            "sctg": [ALL],
            "napcs": [ALL]
        }

class FAFYdm(BaseFreight, DestGeo):
    __tablename__ = "ydm_faf"
    median_moe = 2
    year = db.Column(db.Integer(), primary_key=True)
    transportation_mode = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "destination_geo": [STATE, COUNTY, ALL],
            "sctg": [ALL],
            "transportation_mode": [ALL]
        }

class FAFYom(BaseFreight, OriginGeo):
    __tablename__ = "yom_faf"
    median_moe = 2
    year = db.Column(db.Integer(), primary_key=True)
    transportation_mode = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "origin_geo": [STATE, COUNTY, ALL],
            "sctg": [ALL],
            "transportation_mode": [ALL]
        }
