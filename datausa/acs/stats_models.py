from datausa.acs.abstract_models import GeoId, db
from datausa.core.models import BaseModel
from sqlalchemy.dialects import postgresql
from datausa.attrs import consts


class BaseStat(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "stats"}
    supported_levels = {}
    source_title = 'ACS 5-year Estimate'
    source_link = 'http://www.census.gov/programs-surveys/acs/'
    source_org = 'Census Bureau'


class StateStats(BaseStat, GeoId):
    __tablename__ = "state"
    median_moe = 1.2

    year = db.Column(db.Integer, primary_key=True)
    state_rank = db.Column(db.Integer)
    top_places = db.Column(postgresql.ARRAY(db.String))
    top_counties = db.Column(postgresql.ARRAY(db.String))
    state_neighbors = db.Column(postgresql.ARRAY(db.String))

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [consts.STATE]}


class CountyStats(BaseStat, GeoId):
    __tablename__ = "counties"
    median_moe = 1.2

    year = db.Column(db.Integer, primary_key=True)
    county_state_rank = db.Column(db.Integer)
    places_in_county = db.Column(db.Integer)
    top_places = db.Column(postgresql.ARRAY(db.String))
    county_neighbors = db.Column(postgresql.ARRAY(db.String))

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [consts.COUNTY]}


class MSAStats(BaseStat, GeoId):
    __tablename__ = "msa"
    median_moe = 1.2

    top_counties = db.Column(postgresql.ARRAY(db.String))
    top_places = db.Column(postgresql.ARRAY(db.String))

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [consts.MSA]}


class PlaceStats(BaseStat, GeoId):
    __tablename__ = "place"
    median_moe = 1.2

    parent_counties = db.Column(postgresql.ARRAY(db.String))
    places_neighbors = db.Column(postgresql.ARRAY(db.String))

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [consts.PLACE]}


class PUMAStats(BaseStat, GeoId):
    __tablename__ = "puma"
    median_moe = 1.2

    puma_state_rank = db.Column(db.Integer)
    pumas_in_state = db.Column(db.Integer)
    puma_neighbors = db.Column(postgresql.ARRAY(db.String))

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [consts.PUMA]}
