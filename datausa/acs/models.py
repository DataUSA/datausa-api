from datausa.acs.abstract_models import GeoId, AcsOccId, db, AcsIndId
from datausa.acs.abstract_models import BaseAcs1, BaseAcs3, BaseAcs5
from datausa.acs.abstract_models import Ygl_Speakers
from datausa.attrs import consts
from datausa.attrs.consts import NATION, STATE, MSA, PLACE, PUMA, COUNTY, ALL

class Acs1_Ygl_Speakers(BaseAcs1, Ygl_Speakers):
    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "language": [consts.ALL]}


class Acs5_Ygl_Speakers(BaseAcs5, Ygl_Speakers):
    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS_5YR, "language": [consts.ALL]}


class Acs3_Ygo_Num_Emp(BaseAcs3, GeoId, AcsOccId):
    __tablename__ = "ygo_num_emp"
    median_moe = 2

    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_emp_rca = db.Column(db.Float)
    num_emp_male = db.Column(db.Float)
    num_emp_moe_male = db.Column(db.Float)
    num_emp_female = db.Column(db.Float)
    num_emp_moe_female = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, STATE, MSA, ALL], "acs_occ": AcsOccId.LEVELS}


class Acs5_Ygo_Num_Emp(BaseAcs5, GeoId, AcsOccId):
    __tablename__ = "ygo_num_emp"
    median_moe = 2

    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_emp_rca = db.Column(db.Float)
    num_emp_male = db.Column(db.Float)
    num_emp_moe_male = db.Column(db.Float)
    num_emp_female = db.Column(db.Float)
    num_emp_moe_female = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, COUNTY, MSA, PLACE, PUMA, ALL], "acs_occ": AcsOccId.LEVELS}


class Acs5_Ygo_Earnings(BaseAcs5, GeoId, AcsOccId):
    __tablename__ = "ygo_med_earnings"
    median_moe = 2

    med_earnings = db.Column(db.Float)
    med_earnings_male = db.Column(db.Float)
    med_earnings_female = db.Column(db.Float)
    med_earnings_moe = db.Column(db.Float)
    med_earnings_moe_female = db.Column(db.Float)
    med_earnings_moe_male = db.Column(db.Float)
    med_earnings_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, STATE, COUNTY, MSA, PLACE, PUMA, ALL], "acs_occ": AcsOccId.LEVELS}


class Acs3_Ygi_Num_Emp(BaseAcs3, AcsIndId, GeoId):
    __tablename__ = "ygi_num_emp"
    median_moe = 2

    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_emp_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, STATE, MSA, ALL], "acs_ind": AcsIndId.LEVELS}


class Acs5_Ygi_Num_Emp(BaseAcs5, AcsIndId, GeoId):
    __tablename__ = "ygi_num_emp"
    median_moe = 1.9

    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_emp_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
                "acs_ind": ["0", "1", ALL]}


class Acs3_Ygi_MedEarnings(BaseAcs3, AcsIndId, GeoId):
    __tablename__ = "ygi_med_earnings"
    median_moe = 2

    med_earnings = db.Column(db.Float)
    med_earnings_moe = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, STATE, COUNTY, MSA, PLACE, PUMA, ALL], "acs_ind": ["0", "1", "all"]}
