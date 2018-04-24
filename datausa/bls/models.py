from datausa.database import db
from datausa.attrs.models import Geo, Soc, Naics
from datausa.attrs.models import PumsSoc, PumsNaics
from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, MSA, ALL
from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declared_attr


class Bls(BaseModel):
    source_title = 'Growth'
    source_org = 'Bureau of Labor Statistics'

    __table_args__ = {"schema": "bls"}
    source_link = 'http://bls.gov'


class SocCrosswalk(db.Model, Bls):
    __tablename__ = 'soc_crosswalk'
    soc = db.Column("pums_soc", db.String(), db.ForeignKey(PumsSoc.id), primary_key=True)
    bls_soc = db.Column(db.String(), db.ForeignKey(Soc.id), primary_key=True)


class BlsSoc(object):
    @declared_attr
    def bls_soc(cls):
        return db.Column(db.String(), primary_key=True)

    @declared_attr
    def soc(cls):
        return column_property(SocCrosswalk.soc)

    @classmethod
    def crosswalk_join(cls, qry):
        cond = SocCrosswalk.bls_soc == cls.bls_soc
        return qry.join(SocCrosswalk, cond, full=True)


class GrowthO(db.Model, Bls, BlsSoc):
    source_title = 'Employment Projections'
    __tablename__ = 'growth_o'
    median_moe = 1

    emp_2014_thousands = db.Column(db.Float)
    emp_2024_thousands = db.Column(db.Float)
    emp_pct_2014 = db.Column(db.Float)
    emp_pct_2024 = db.Column(db.Float)
    change_thousands = db.Column(db.Float)
    pct_change = db.Column(db.Float)
    openings_thousands = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "soc": [ALL, "0", "1", "2", "3"],
            "bls_soc": [ALL, "0", "1", "2", "3"]
        }


class GrowthO16(db.Model, Bls, BlsSoc):
    source_title = 'Employment Projections'
    __tablename__ = 'growth_o_2016'
    median_moe = 1

    emp_2016_thousands = db.Column(db.Float)
    emp_2026_thousands = db.Column(db.Float)
    emp_pct_2016 = db.Column(db.Float)
    emp_pct_2026 = db.Column(db.Float)
    change_thousands = db.Column(db.Float)
    pct_change = db.Column(db.Float)
    openings_thousands = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "soc": [ALL, "0", "1", "2", "3"],
            "bls_soc": [ALL, "0", "1", "2", "3"]
        }


class GrowthI(db.Model, Bls):
    source_title = 'Industry Projections'
    __tablename__ = 'growth_i'
    median_moe = 2

    naics = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    emp_2004_thousands = db.Column(db.Float)
    emp_2014_thousands = db.Column(db.Float)
    emp_2024_thousands = db.Column(db.Float)
    emp_change_2004_2014 = db.Column(db.Float)
    emp_change_2014_2024 = db.Column(db.Float)
    output_2004 = db.Column(db.Float)
    output_2014 = db.Column(db.Float)
    output_2024 = db.Column(db.Float)
    output_carc_2004_2014 = db.Column(db.Float)
    output_carc_2014_2024 = db.Column(db.Float)
    emp_carc_2004_2014 = db.Column(db.Float)
    emp_carc_2014_2024 = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "naics": [ALL, "0", "1", "2", "3", "4"]
        }


class GrowthI16(db.Model, Bls):
    source_title = 'Industry Projections'
    __tablename__ = 'growth_i_2016'
    median_moe = 2

    naics = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    emp_2006_thousands = db.Column(db.Float)
    emp_2016_thousands = db.Column(db.Float)
    emp_2026_thousands = db.Column(db.Float)
    emp_change_2006_2016 = db.Column(db.Float)
    emp_change_2016_2026 = db.Column(db.Float)
    output_2006 = db.Column(db.Float)
    output_2016 = db.Column(db.Float)
    output_2026 = db.Column(db.Float)
    output_carc_2006_2016 = db.Column(db.Float)
    output_carc_2016_2026 = db.Column(db.Float)
    emp_carc_2006_2016 = db.Column(db.Float)
    emp_carc_2016_2026 = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "naics": [ALL, "0", "1", "2", "3", "4"]
        }


class BlsCrosswalk(db.Model, Bls):
    __tablename__ = 'bls_crosswalk'
    pums_naics = db.Column(db.String, db.ForeignKey(PumsNaics.id),
                           primary_key=True)
    bls_naics = db.Column(db.String, primary_key=True)


class GrowthILookup(db.Model, Bls):
    __tablename__ = 'growth_i_lookup'
    pums_naics = db.Column(db.String, db.ForeignKey(PumsNaics.id), primary_key=True)
    bls_naics = db.Column(db.String, primary_key=True)


class OesYgo(db.Model, Bls, BlsSoc):
    __tablename__ = 'oes_ygo'

    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    geo = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    # soc = db.Column(db.String, db.ForeignKey(Soc.id), primary_key=True)

    tot_emp = db.Column(db.Integer)
    tot_emp_prse = db.Column(db.Float)
    avg_wage = db.Column(db.Float)
    avg_wage_prse = db.Column(db.Float)
    tot_emp_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [ALL, NATION, STATE, MSA],
            "bls_soc": [ALL, "0", "1", "2", "3"],
            "soc": [ALL, "0", "1", "2", "3"]
        }

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {NATION: "010", STATE: "040", MSA: "050"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)


class CesYi(db.Model, Bls):
    source_title = 'Current Employment Statistics'
    __tablename__ = 'ces_yi'
    median_moe = 1.5

    JOINED_FILTER = {"naics": {
                     "table": Naics,
                     "column": Naics.level,
                     "id": Naics.id}}

    year = db.Column(db.Integer, primary_key=True)
    naics = db.Column(db.String, db.ForeignKey(Naics.id), primary_key=True)

    avg_hrly_earnings = db.Column(db.Float)
    avg_wkly_hrs = db.Column(db.Float)
    employees_thousands = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "naics": [ALL, "0", "1", "2", "3", "4"]
        }


class QcewYgi(db.Model, Bls):
    __tablename__ = 'qcew_ygi'
    median_moe = 2

    year = db.Column(db.Integer, primary_key=True)
    geo = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    naics = db.Column(db.String, db.ForeignKey(Naics.id), primary_key=True)

    naics_level = db.Column(db.Integer)
    avg_annual_pay = db.Column(db.Float)
    total_annual_wages = db.Column(db.Float)
    annual_contributions = db.Column(db.Float)
    annual_avg_emplvl = db.Column(db.Float)
    total_annual_wages_rca = db.Column(db.Float)
    annual_avg_estabs = db.Column(db.Float)
    taxable_annual_wages = db.Column(db.Float)
    annual_avg_wkly_wage = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {
            "geo": [ALL, NATION, STATE, MSA],
            "naics": [ALL, "0", "1", "2", "3", "4"]
        }

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {NATION: "010", STATE: "040", MSA: "050"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)

    @classmethod
    def naics_filter(cls, level):
        if level == ALL:
            return True
        return cls.naics_level == level
