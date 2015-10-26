from datausa.acs.abstract_models import BaseAcs5, GeoId, AcsOccId
from datausa.acs.abstract_models import db


class Acs5_Yg(BaseAcs5, GeoId):
    __tablename__ = "yg"
    median_moe = 1

    year = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Float)
    age_moe = db.Column(db.Float)
    age_rank = db.Column(db.Integer)
    pop = db.Column(db.Float)
    pop_moe = db.Column(db.Float)
    pop_rank = db.Column(db.Integer)
    income = db.Column(db.Float)
    income_moe = db.Column(db.Float)
    income_rank = db.Column(db.Integer)


class Acs5_Yg_Income(BaseAcs5, GeoId):
    __tablename__ = "yg_income"
    median_moe = 1.2

    year = db.Column(db.Integer, primary_key=True)
    income = db.Column(db.Float)
    income_moe = db.Column(db.Float)


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

class Acs5_Yg_Conflict(BaseAcs5, GeoId):
    __tablename__ = "yg_conflict"
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    total_vets = db.Column(db.Float)
    total_vets_moe = db.Column(db.Float)
    wwii = db.Column(db.Float)
    wwii_moe = db.Column(db.Float)
    korea = db.Column(db.Float)
    korea_moe = db.Column(db.Float)
    vietnam = db.Column(db.Float)
    vietnam_moe = db.Column(db.Float)
    gulf90s = db.Column(db.Float)
    gulf90s_moe = db.Column(db.Float)
    gulf01 = db.Column(db.Float)
    gulf01_moe = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS}


class Acs5_Yg_IncDist(BaseAcs5, GeoId):
    __tablename__ = "yg_income_distribution"
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    income100to125 = db.Column(db.Float)
    income100to125_moe = db.Column(db.Float)
    income10to15 = db.Column(db.Float)
    income10to15_moe = db.Column(db.Float)
    income125to150 = db.Column(db.Float)
    income125to150_moe = db.Column(db.Float)
    income150to200 = db.Column(db.Float)
    income150to200_moe = db.Column(db.Float)
    income15to20 = db.Column(db.Float)
    income15to20_moe = db.Column(db.Float)
    income200more = db.Column(db.Float)
    income200more_moe = db.Column(db.Float)
    income20to25 = db.Column(db.Float)
    income20to25_moe = db.Column(db.Float)
    income25to30 = db.Column(db.Float)
    income25to30_moe = db.Column(db.Float)
    income30to35 = db.Column(db.Float)
    income30to35_moe = db.Column(db.Float)
    income35to40 = db.Column(db.Float)
    income35to40_moe = db.Column(db.Float)
    income40to45 = db.Column(db.Float)
    income40to45_moe = db.Column(db.Float)
    income45to50 = db.Column(db.Float)
    income45to50_moe = db.Column(db.Float)
    income50to60 = db.Column(db.Float)
    income50to60_moe = db.Column(db.Float)
    income60to75 = db.Column(db.Float)
    income60to75_moe = db.Column(db.Float)
    income75to100 = db.Column(db.Float)
    income75to100_moe = db.Column(db.Float)
    incomeless10 = db.Column(db.Float)
    incomeless10_moe = db.Column(db.Float)
    totalhouseholds = db.Column(db.Float)
    totalhouseholds_moe = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS}
