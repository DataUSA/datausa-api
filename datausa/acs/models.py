from datausa.acs.abstract_models import GeoId, AcsOccId, db, AcsIndId
from datausa.acs.abstract_models import BaseAcs1, BaseAcs3, BaseAcs5
from datausa.acs.abstract_models import Ygl_Speakers, GeoId5, GeoId1, BaseHealth
from datausa.attrs import consts
from datausa.attrs.consts import NATION, STATE, MSA, PLACE, PUMA, COUNTY, ALL

class Acs1_Ygi_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "ygi_health"
    median_moe = 2

    insurance = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "insurance": [ALL]
        }

class Acs1_Yga_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "yga_health"
    median_moe = 2

    age_bucket = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "age_bucket": [ALL]
        }

class Acs1_Ygai_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "ygai_health"
    median_moe = 3

    age_bucket = db.Column(db.String(), primary_key=True)
    insurance = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "insurance": [ALL],
            "age_bucket": [ALL]
        }


class Acs1_Ygis_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "ygis_health"
    median_moe = 3

    sex = db.Column(db.String(), primary_key=True)
    insurance = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "insurance": [ALL],
            "sex": [ALL]
        }



class Acs1_Ygas_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "ygas_health"
    median_moe = 3

    sex = db.Column(db.String(), primary_key=True)
    age_bucket = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "sex": [ALL],
            "age_bucket": [ALL]
        }

class Acs1_Ygs_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "ygs_health"
    median_moe = 2

    sex = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "sex": [ALL]
        }


class Acs1_Ygais_Health(BaseAcs1, GeoId1, BaseHealth):
    __tablename__ = "ygais_health"
    median_moe = 4

    sex = db.Column(db.String(), primary_key=True)
    age_bucket = db.Column(db.String(), primary_key=True)
    insurance = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
            "sex": [ALL],
            "insurance": [ALL],
            "age_bucket": [ALL]
        }



class Acs1_Ygl_Speakers(BaseAcs1, GeoId1, Ygl_Speakers):
    __tablename__ = "ygl_speakers"
    median_moe = 2.2

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS_1YR, "language": [consts.ALL]}

class Acs5_Ygl_Speakers(BaseAcs5, GeoId5, Ygl_Speakers):
    __tablename__ = "ygl_speakers"
    median_moe = 2

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


class Acs1_Ygo_Num_Emp(BaseAcs1, GeoId, AcsOccId):
    __tablename__ = "ygo_num_emp"
    median_moe = 2.5

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


class Acs1_Ygo_Earnings(BaseAcs1, GeoId, AcsOccId):
    __tablename__ = "ygo_med_earnings"
    median_moe = 2.5

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


class Acs1_Ygi_Num_Emp(BaseAcs1, AcsIndId, GeoId):
    __tablename__ = "ygi_num_emp"
    median_moe = 2.5

    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_emp_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL],
                "acs_ind": ["0", "1", ALL]}


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


class Acs1_Yg_Num_Emp(BaseAcs1, GeoId):
    __tablename__ = "yg_num_emp"
    median_moe = 1.2

    civ_labor_force = db.Column(db.Float)
    civ_labor_force_moe = db.Column(db.Float)
    emp_survey_total = db.Column(db.Float)
    emp_survey_total_moe = db.Column(db.Float)
    labor_force = db.Column(db.Float)
    labor_force_moe = db.Column(db.Float)
    not_in_labor_force = db.Column(db.Float)
    not_in_labor_force_moe = db.Column(db.Float)
    num_armed_forces = db.Column(db.Float)
    num_armed_forces_moe = db.Column(db.Float)
    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_unemp = db.Column(db.Float)
    num_unemp_moe = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, COUNTY, MSA, PLACE, PUMA, ALL], "acs_occ": AcsOccId.LEVELS}


class Acs5_Yg_Num_Emp(BaseAcs5, GeoId):
    __tablename__ = "yg_num_emp"
    median_moe = 1

    civ_labor_force = db.Column(db.Float)
    civ_labor_force_moe = db.Column(db.Float)
    emp_survey_total = db.Column(db.Float)
    emp_survey_total_moe = db.Column(db.Float)
    labor_force = db.Column(db.Float)
    labor_force_moe = db.Column(db.Float)
    not_in_labor_force = db.Column(db.Float)
    not_in_labor_force_moe = db.Column(db.Float)
    num_armed_forces = db.Column(db.Float)
    num_armed_forces_moe = db.Column(db.Float)
    num_emp = db.Column(db.Float)
    num_emp_moe = db.Column(db.Float)
    num_unemp = db.Column(db.Float)
    num_unemp_moe = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": [NATION, COUNTY, MSA, PLACE, PUMA, ALL], "acs_occ": AcsOccId.LEVELS}
