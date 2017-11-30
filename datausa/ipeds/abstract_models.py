from datausa.database import db
from datausa.attrs.models import University, Cip, Geo, EnrollmentStatus
from datausa.attrs.models import Degree, Sector, LStudy
from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA
from datausa.attrs.consts import PUMA, PLACE, ALL, GEO

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func


class BaseIpeds(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "ipeds"}
    supported_levels = {}
    source_title = 'NCES IPEDS'
    source_link = 'http://nces.ed.gov/ipeds/'
    source_org = 'Department of Education'


class Enrollment(BaseIpeds):
    __abstract__ = True

    enrolled_total = db.Column(db.Integer())
    enrolled_men = db.Column(db.Integer())
    enrolled_women = db.Column(db.Integer())
    enrolled_black = db.Column(db.Integer())
    enrolled_asian = db.Column(db.Integer())
    enrolled_native = db.Column(db.Integer())
    enrolled_unknown = db.Column(db.Integer())


class Tuition(BaseIpeds):
    __abstract__ = True

    oos_tuition = db.Column(db.Integer())
    state_tuition = db.Column(db.Integer())
    district_tuition = db.Column(db.Integer())

    oos_fee = db.Column(db.Integer())
    state_fee = db.Column(db.Integer())
    district_fee = db.Column(db.Integer())


class GradsPct(BaseIpeds):
    __abstract__ = True
    pct_total = db.Column(db.Float())
    pct_men = db.Column(db.Float())
    pct_women = db.Column(db.Float())


class Grads(BaseIpeds):
    __abstract__ = True
    grads_total = db.Column(db.Integer())
    grads_men = db.Column(db.Integer())
    grads_women = db.Column(db.Integer())
    grads_native = db.Column(db.Integer())
    grads_native_men = db.Column(db.Integer())
    grads_native_women = db.Column(db.Integer())
    grads_asian = db.Column(db.Integer())
    grads_asian_men = db.Column(db.Integer())
    grads_asian_women = db.Column(db.Integer())
    grads_black = db.Column(db.Integer())
    grads_black_men = db.Column(db.Integer())
    grads_black_women = db.Column(db.Integer())
    grads_hispanic = db.Column(db.Integer())
    grads_hispanic_men = db.Column(db.Integer())
    grads_hispanic_women = db.Column(db.Integer())
    grads_hawaiian = db.Column(db.Integer())
    grads_hawaiian_men = db.Column(db.Integer())
    grads_hawaiian_women = db.Column(db.Integer())
    grads_white = db.Column(db.Integer())
    grads_white_men = db.Column(db.Integer())
    grads_white_women = db.Column(db.Integer())
    grads_multi = db.Column(db.Integer())
    grads_multi_men = db.Column(db.Integer())
    grads_multi_women = db.Column(db.Integer())
    grads_unknown = db.Column(db.Integer())
    grads_unknown_men = db.Column(db.Integer())
    grads_unknown_women = db.Column(db.Integer())
    grads_nonresident = db.Column(db.Integer())
    grads_nonresident_men = db.Column(db.Integer())
    grads_nonresident_women = db.Column(db.Integer())


class GeoId(object):
    LEVELS = [NATION, STATE, COUNTY, PLACE, MSA, PUMA, ALL]

    @declared_attr
    def geo(cls):
        return db.Column(db.String(), db.ForeignKey(Geo.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {GEO: GeoId.LEVELS}

    @classmethod
    def geo_filter(cls, level):
        if level == ALL:
            return True
        level_map = {NATION: "010", STATE: "040", PUMA: "795",
                     COUNTY: "050", MSA: "310", PLACE: "160"}
        level_code = level_map[level]
        return cls.geo.startswith(level_code)


class CipId(object):
    LEVELS = ["2", "4", "6", "all"]

    @declared_attr
    def cip(cls):
        return db.Column(db.String(), db.ForeignKey(Cip.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["all", "2", "4", "6"]}

    @classmethod
    def cip_filter(cls, level):
        if level == 'all':
            return True
        return func.length(cls.cip) == level


class UniversityId(object):
    LEVELS = ["all", "0", "1", "2"]
    # TODO add university level filter ...

    @declared_attr
    def university(cls):
        return db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)

    @declared_attr
    def university_level(cls):
        return db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS}

    @classmethod
    def university_filter(cls, level):
        if level == 'all':
            return True
        return cls.university_level == level


class LStudyId(object):
    @declared_attr
    def lstudy(cls):
        return db.Column(db.String(), db.ForeignKey(LStudy.id), primary_key=True)


class EnrollmentStatusId(object):
    @declared_attr
    def enrollment_status(cls):
        return db.Column(db.String(), db.ForeignKey(EnrollmentStatus.id), primary_key=True)


class DegreeId(object):
    @declared_attr
    def degree(cls):
        return db.Column(db.String(), db.ForeignKey(Degree.id), primary_key=True)


class SectorId(object):
    @declared_attr
    def sector(cls):
        return db.Column(db.String(), db.ForeignKey(Sector.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"sector": ["all"]}


class Admissions(BaseIpeds):
    __abstract__ = True
    applicants_total = db.Column(db.Float)
    applicants_men = db.Column(db.Float)
    applicants_women = db.Column(db.Float)
    admissions_total = db.Column(db.Float)
    admissions_men = db.Column(db.Float)
    admissions_women = db.Column(db.Float)
    admissions_enrolled_total = db.Column(db.Float)
    admissions_enrolled_men = db.Column(db.Float)
    admissions_enrolled_women = db.Column(db.Float)
    admissions_enrolled_ft_total = db.Column(db.Float)
    admissions_enrolled_ft_men = db.Column(db.Float)
    admissions_enrolled_ft_women = db.Column(db.Float)
    admissions_enrolled_pt_total = db.Column(db.Float)
    admissions_enrolled_pt_men = db.Column(db.Float)
    admissions_enrolled_pt_women = db.Column(db.Float)
    sub_sat_scores_num = db.Column(db.Float)
    sub_act_scores_num = db.Column(db.Float)
    sub_sat_scores_pct = db.Column(db.Float)
    sub_act_scores_pct = db.Column(db.Float)
    sat_cr_25 = db.Column(db.Float)
    sat_cr_75 = db.Column(db.Float)
    sat_math_25 = db.Column(db.Float)
    sat_math_75 = db.Column(db.Float)
    sat_writing_25 = db.Column(db.Float)
    sat_writing_75 = db.Column(db.Float)
    act_composite_25 = db.Column(db.Float)
    act_composite_75 = db.Column(db.Float)
    act_english_25 = db.Column(db.Float)
    act_english_75 = db.Column(db.Float)
    act_math_25 = db.Column(db.Float)
    act_math_75 = db.Column(db.Float)
    act_writing_25 = db.Column(db.Float)
    act_writing_75 = db.Column(db.Float)
    yield_total = db.Column(db.Float)
    yield_men = db.Column(db.Float)
    yield_women = db.Column(db.Float)


class EnrollmentEfa(BaseIpeds):
    __abstract__ = True
    enrolled_total = db.Column(db.Float)
    enrolled_men = db.Column(db.Float)
    enrolled_women = db.Column(db.Float)
    enrolled_native = db.Column(db.Float)
    enrolled_native_men = db.Column(db.Float)
    enrolled_native_women = db.Column(db.Float)
    enrolled_asian = db.Column(db.Float)
    enrolled_asian_men = db.Column(db.Float)
    enrolled_asian_women = db.Column(db.Float)
    enrolled_black = db.Column(db.Float)
    enrolled_black_men = db.Column(db.Float)
    enrolled_black_women = db.Column(db.Float)
    enrolled_hispanic = db.Column(db.Float)
    enrolled_hispanic_men = db.Column(db.Float)
    enrolled_hispanic_women = db.Column(db.Float)
    enrolled_hawaiian = db.Column(db.Float)
    enrolled_hawaiian_men = db.Column(db.Float)
    enrolled_enrolled_hawaiian_women = db.Column(db.Float)
    enrolled_white = db.Column(db.Float)
    enrolled_white_men = db.Column(db.Float)
    enrolled_white_women = db.Column(db.Float)
    enrolled_multiracial = db.Column(db.Float)
    enrolled_multiracial_men = db.Column(db.Float)
    enrolled_multiracial_women = db.Column(db.Float)
    enrolled_unknown = db.Column(db.Float)
    enrolled_unknown_men = db.Column(db.Float)
    enrolled_unknown_women = db.Column(db.Float)
    enrolled_nonresident = db.Column(db.Float)
    enrolled_nonresident_men = db.Column(db.Float)
    enrolled_nonresident_women = db.Column(db.Float)
