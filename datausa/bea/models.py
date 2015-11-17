from datausa.database import db
from datausa.attrs.models import IoCode
from datausa.core.models import BaseModel
from datausa.attrs.consts import ALL
# from sqlalchemy import and_

class BeaUse(db.Model, BaseModel):
    __table_args__ = {"schema": "bea"}
    __tablename__ = 'use'
    source_title = 'Bureau of Economic Analysis'
    source_link = 'http://bea.gov'

    median_moe = 2
    to_filter = ["F07S", "TOTCOMOUT", "F010", "F07C", "F02S", "HS", "F06N", "F02E", "F07E", "F10N", "F06E",
                 "F10C","F030", "F10E", "TOTFU", "F050", "F06S", "ORE", "F02R", "F040", "F06C", "GFGD", "F020",
                 "G", "F07N","F02N", "TOTII", "F10S", "F100", "GFGN", "GSLE", "GFE", "GSLG", "Other", "Used",
                 "V001", "V002", "V003", "TOTCOMOUT", "TOTFU", "TOTII", "TOTINDOUT", "TOTVA"]
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
