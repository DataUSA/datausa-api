from datausa.database import db
from datausa.attrs.models import Geo, Soc
from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, MSA, ALL

from datausa.cbp.abstract_models import BaseCbp
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA
from sqlalchemy.sql import func

class CbpYgi(BaseCbp):
    __tablename__ = "ygi"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    geo_id = db.Column(db.String(), primary_key=True)
    naics = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo_id": [ALL, NATION, STATE, MSA, COUNTY],
            "naics": [ALL, "0", "1", "2", "3", "4"]
        }

    @classmethod
    def naics_filter(cls, level):
        if level == ALL:
            return True
        target_len = int(level) + 2
        return func.length(cls.naics) == target_len

class CbpYg(BaseCbp):
    __tablename__ = "yg"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    geo_id = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo_id": [ALL, NATION, STATE, MSA, COUNTY],
        }
