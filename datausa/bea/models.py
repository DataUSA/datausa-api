from datausa.database import db
from datausa.attrs.models import IoCode
from datausa.core.models import BaseModel
from datausa.attrs.consts import ALL
# from sqlalchemy import and_

class BeaUse(db.Model, BaseModel):
    __table_args__ = {"schema": "bea"}
    __tablename__ = 'use'
    source_title = 'Use Tables'
    source_link = 'http://bea.gov'
    source_org = 'Bureau of Economic Analysis'

    median_moe = 2
    to_filter = ["TOTCOMOUT", "HS", "ORE", "GFGD", "G", "TOTII", "GFGN", "GSLE",
                 "GFE", "GSLG", "Other", "Used", "TOTFU", "V001", "V002",
                 "V003", "TOTINDOUT", "TOTVA"]
    year = db.Column(db.Integer, primary_key=True)
    industry_iocode = db.Column(db.String, db.ForeignKey(IoCode.id), primary_key=True)
    commodity_iocode = db.Column(db.String, db.ForeignKey(IoCode.id), primary_key=True)

    value_millions = db.Column(db.Integer)
    industry_level = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "industry_iocode": [ALL, "0", "1", "naics"],
            "commodity_iocode": [ALL, "naics"],
        }

    @classmethod
    def industry_iocode_filter(cls, level):
        if level == ALL:
            return True
        elif level == "naics":
            return ~cls.industry_iocode.in_(cls.to_filter)
        target_len = int(level)
        return cls.industry_level == target_len

    @classmethod
    def commodity_iocode_filter(cls, level):
        if level == ALL:
            return True
        return ~cls.commodity_iocode.in_(cls.to_filter)
