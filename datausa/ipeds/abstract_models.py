from datausa.database import db
from datausa.attrs.models import University, Cip, Geo, EnrollmentStatus
from datausa.attrs.models import Degree, Sector, LStudy, IPedsRace, IPedsOcc
from datausa.attrs.models import LivingArrangement, IncomeRange, AcademicRank
from datausa.attrs.models import IPedsExpense
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

    oos_tuition_grads = db.Column(db.Integer())
    state_tuition_grads = db.Column(db.Integer())
    district_tuition_grads = db.Column(db.Integer())

    oos_fee_grads = db.Column(db.Integer())
    state_fee_grads = db.Column(db.Integer())
    district_fee_grads = db.Column(db.Integer())

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


class IPedsRaceId(object):
    @declared_attr
    def ipeds_race(cls):
        return db.Column(db.String(), db.ForeignKey(IPedsRace.id), primary_key=True)


class EnrollmentEfa(BaseIpeds):
    __abstract__ = True
    num_enrolled = db.Column(db.Float)


class LivingArrangementId(object):
    @declared_attr
    def living_arrangement(cls):
        return db.Column(db.String(), db.ForeignKey(LivingArrangement.id), primary_key=True)


class IncomeRangeId(object):
    @declared_attr
    def income_range(cls):
        return db.Column(db.String(), db.ForeignKey(IncomeRange.id), primary_key=True)


class SfaLivingBase(BaseIpeds):
    __abstract__ = True
    num_in_living_arrangement = db.Column(db.Float)


class GradRateBase(BaseIpeds):
    __abstract__ = True
    grad_rate = db.Column(db.Float)
    cohort_size = db.Column(db.Float)
    num_finishers = db.Column(db.Float)


class FinancialsBase(BaseIpeds):
    __abstract__ = True
    endowment_value_fiscal_year_end = db.Column(db.Float)
    federal_grants_and_contracts = db.Column(db.Float)
    investment_income = db.Column(db.Float)
    local_grants = db.Column(db.Float)
    local_grants_and_contracts = db.Column(db.Float)
    other_federal_grants = db.Column(db.Float)
    pell_grants = db.Column(db.Float)
    private_grants = db.Column(db.Float)
    research_rank = db.Column(db.Float)
    research_rank_carnegie = db.Column(db.Float)
    research_rank_carnegie_pct = db.Column(db.Float)
    research_rank_pct = db.Column(db.Float)
    research_total = db.Column(db.Float)
    state_grants = db.Column(db.Float)
    state_grants_and_contracts = db.Column(db.Float)
    total_expenses = db.Column(db.Float)
    tuition_and_fees = db.Column(db.Float)
    total_salaries = db.Column(db.Float)


class ExpensesBase(BaseIpeds):
    __abstract__ = True
    benefits_expense = db.Column(db.Float)
    dep_expense = db.Column(db.Float)
    interest_expense = db.Column(db.Float)
    ops_expense = db.Column(db.Float)
    other_expense = db.Column(db.Float)
    salaries_expense = db.Column(db.Float)


class NISSalariesBase(BaseIpeds):
    __abstract__ = True
    num_noninstructional_staff = db.Column(db.Float)
    outlays_noninstructional_staff = db.Column(db.Float)


class ISSalariesBase(BaseIpeds):
    __abstract__ = True
    num_instructional_staff = db.Column(db.Float)
    outlays_instructional_staff = db.Column(db.Float)
    months_covered_instructional_staff = db.Column(db.Float)


class IPedsOccId(object):
    @declared_attr
    def ipeds_occ(cls):
        return db.Column(db.String(), db.ForeignKey(IPedsOcc.id), primary_key=True)


class AcademicRankId(object):
    @declared_attr
    def academic_rank(cls):
        return db.Column(db.String(), db.ForeignKey(AcademicRank.id), primary_key=True)


class IPedsExpenseId(object):
    @declared_attr
    def ipeds_expense(cls):
        return db.Column(db.String(), db.ForeignKey(IPedsExpense.id), primary_key=True)
