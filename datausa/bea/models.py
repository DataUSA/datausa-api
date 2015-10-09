from datausa.database import db
from datausa.attrs.models import IoCode, Soc
from datausa.core.models import BaseModel
from datausa.attrs.consts import ALL
from sqlalchemy.sql import func

class BeaUse(db.Model, BaseModel):
    __table_args__ = {"schema": "bea"}
    __tablename__ = 'use'
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    industry_iocode = db.Column(db.String, db.ForeignKey(IoCode.id), primary_key=True)
    commodity_iocode = db.Column(db.String, db.ForeignKey(IoCode.id), primary_key=True)

    value_millions = db.Column(db.Integer)
    industry_level = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "industry_iocode": [ALL, "0", "1"],
        }

    @classmethod
    def industry_iocode_filter(cls, level):
        if level == ALL:
            return True
        target_len = int(level)
        return cls.industry_level == target_len
