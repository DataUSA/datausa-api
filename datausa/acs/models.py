from datausa.acs.abstract_models import BaseAcs5, GeoId, AcsOccId
from datausa.acs.abstract_models import db
from datausa.attrs.models import AcsLanguage
from datausa.attrs import consts


class Acs5_Ygl_Speakers(BaseAcs5, GeoId):
    __tablename__ = "ygl_speakers"
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(), db.ForeignKey(AcsLanguage.id), primary_key=True)
    num_speakers = db.Column(db.Float)
    num_speakers_moe = db.Column(db.Float)
    num_speakers_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "language": [consts.ALL]}


class Acs5_Ygo_Num_Emp(BaseAcs5, GeoId, AcsOccId):
    __tablename__ = "ygo_num_emp"
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_emp_rca = db.Column(db.Float)
    num_emp_male = db.Column(db.Float)
    num_emp_moe_male = db.Column(db.Float)
    num_emp_female = db.Column(db.Float)
    num_emp_moe_female = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "acs_occ": AcsOccId.LEVELS}


class Acs5_Ygo_Earnings(BaseAcs5, GeoId, AcsOccId):
    __tablename__ = "ygo_earnings"
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    earnings = db.Column(db.Float)
    earnings_moe = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "acs_occ": AcsOccId.LEVELS}
