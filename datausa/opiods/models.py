from datausa.database import db
from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, ALL
from datausa.attrs.models import Geo
from sqlalchemy.ext.declarative import declared_attr


class BaseOpiods(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "opiods"}
    supported_levels = {"year": [ALL]}
    source_title = 'Opiods Data'
    source_link = 'https://datausa.io'
    source_org = 'Deloitte'

    default_rate = db.Column(db.Float)
    num_defaults = db.Column(db.Integer)
    num_borrowers = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "year": [ALL],
            "geo": [ALL, NATION, STATE]
        }

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {STATE: "040", NATION: "010"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)

    @declared_attr
    def geo(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)


class DrugOverdoseDeathRate(BaseOpiods):
    __tablename__ = "drug_overdose_deathrate"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    drug_overdose_ageadjusted = db.Column(db.String())

    # @classmethod
    # def get_supported_levels(cls):
    #     return {
    #         "university": [ALL],
    #         "opeid": [ALL],
    #     }
