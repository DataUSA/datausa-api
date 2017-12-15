from datausa.database import db
from datausa.ipeds.abstract_models import CipId, UniversityId
from datausa.ipeds.abstract_models import Tuition, GeoId, SectorId, BaseIpeds
from datausa.ipeds.abstract_models import Grads, DegreeId, GradsPct, Admissions
from datausa.ipeds.abstract_models import EnrollmentEfa, LStudyId, EnrollmentStatusId, IPedsRaceId
from datausa.ipeds.abstract_models import SfaLivingBase, GradRateBase, LivingArrangementId
from datausa.ipeds.abstract_models import FinancialsBase, IncomeRangeId
from datausa.pums.abstract_models import SexId

from datausa.attrs.consts import STATE, COUNTY, MSA, GEO
from datausa.attrs.consts import PLACE, ALL


# class EnrollmentYcu(Enrollment, CipId, UniversityId):
#     __tablename__ = "enrollment_ycu"
#     median_moe = 2.1
#
#     year = db.Column(db.Integer(), primary_key=True)
#     grads_total = db.Column(db.Integer())
#
#     @classmethod
#     def get_supported_levels(cls):
#         return {"cip": CipId.LEVELS, "university": UniversityId.LEVELS}


class TuitionYgs(Tuition, GeoId, SectorId):
    __tablename__ = "tuition_ygs"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "sector": [ALL]}


class TuitionYc(Tuition, CipId):
    __tablename__ = "tuition_yc"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    oos_tuition_rank = db.Column(db.Integer())
    state_tuition_rank = db.Column(db.Integer())


class TuitionYu(Tuition, UniversityId):
    __tablename__ = "tuition_yu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS}


class TuitionYcu(Tuition, CipId, UniversityId):
    __tablename__ = "tuition_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": UniversityId.LEVELS}


class TuitionYcs(Tuition, CipId, SectorId):
    __tablename__ = "tuition_ycs"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    num_universities = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "sector": [ALL]}


class GradsYc(Grads, CipId):
    __tablename__ = "grads_yc"
    median_moe = 0

    year = db.Column(db.Integer(), primary_key=True)
    grads_rank = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS}


class GradsYcd(Grads, CipId, DegreeId):
    __tablename__ = "grads_ycd"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "degree": [ALL]}


class GradsYu(Grads, UniversityId):
    __tablename__ = "grads_yu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS}


class GradsYcu(Grads, CipId, UniversityId):
    __tablename__ = "grads_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)

    # parent = relationship('Geo', foreign_keys='GeoContainment.parent_geoid')

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": UniversityId.LEVELS,
                GEO: [STATE, COUNTY, MSA, PLACE, ALL]}


class GradsYg(Grads, GeoId):
    __tablename__ = "grads_yg"
    median_moe = 1

    year = db.Column(db.Integer, primary_key=True)
    grads_total_growth = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {GEO: GeoId.LEVELS}


class GradsYgc(Grads, GeoId, CipId):
    __tablename__ = "grads_ygc"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total_growth = db.Column(db.Float)
    grads_total_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, GEO: GeoId.LEVELS}


class GradsYgu(Grads, GeoId, UniversityId):
    __tablename__ = "grads_ygu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total_growth = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS, GEO: GeoId.LEVELS}


class GradsYgs(Grads, GeoId, SectorId):
    __tablename__ = "grads_ygs"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total_growth = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"sector": [ALL], GEO: GeoId.LEVELS}


class GradsYud(Grads, UniversityId, DegreeId):
    __tablename__ = "grads_yud"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS, "degree": [ALL]}


class GradsYucd(Grads, UniversityId, CipId, DegreeId):
    __tablename__ = "grads_yucd"
    median_moe = 3

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer())

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS, "degree": [ALL], "cip": CipId.LEVELS}


class GradsYgd(Grads, GeoId, DegreeId):
    __tablename__ = "grads_ygd"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total_growth = db.Column(db.Float)
    grads_total_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {GEO: GeoId.LEVELS, "degree": [ALL]}


class GradsYgcd(Grads, GeoId, CipId, DegreeId):
    __tablename__ = "grads_ygcd"
    median_moe = 3

    year = db.Column(db.Integer(), primary_key=True)
    grads_total_growth = db.Column(db.Float)
    grads_total_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, GEO: GeoId.LEVELS, "degree": [ALL]}


class GradsPctYcu(GradsPct, CipId, UniversityId):
    __tablename__ = "gradspct_ycu"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    grads_total = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": CipId.LEVELS, "university": UniversityId.LEVELS}


class UnivGeo(BaseIpeds, UniversityId, GeoId):
    __tablename__ = "university_geo"
    median_moe = 0

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS,
                GEO: [STATE, COUNTY, MSA, PLACE, ALL]}


class AdmissionsYu(Admissions, UniversityId):
    __tablename__ = "adm_undergrad_yu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"university": UniversityId.LEVELS}


class AdmissionsY(Admissions):
    __tablename__ = "adm_undergrad_y"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 0

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL]}


class EnrollmentEfaYus(EnrollmentEfa, UniversityId, SexId):
    __tablename__ = "enrollment_efa_yus"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "sex": [ALL]}


class EnrollmentEfaYur(EnrollmentEfa, UniversityId, IPedsRaceId):
    __tablename__ = "enrollment_efa_yur"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "ipeds_race": [ALL]}


class EnrollmentEfaYue(EnrollmentEfa, UniversityId, EnrollmentStatusId):
    __tablename__ = "enrollment_efa_yue"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "enrollment_status": [ALL]}


class EnrollmentEfaYul(EnrollmentEfa, UniversityId, LStudyId):
    __tablename__ = "enrollment_efa_yul"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "lstudy": [ALL]}


class EnrollmentEfaYusrl(EnrollmentEfa, UniversityId, SexId, IPedsRaceId, LStudyId):
    __tablename__ = "enrollment_efa_yusrl"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 5

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "sex": [ALL],
                "ipeds_race": [ALL],
                "lstudy": [ALL]}


class EnrollmentEfaYusrle(EnrollmentEfa, UniversityId, SexId, IPedsRaceId, LStudyId, EnrollmentStatusId):
    __tablename__ = "enrollment_efa_yusrle"
    year = db.Column(db.Integer(), primary_key=True)
    median_moe = 5

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "sex": [ALL],
                "ipeds_race": [ALL],
                "lstudy": [ALL],
                "enrollment_status": [ALL]}


class LivingArrangementSfaYu(SfaLivingBase, UniversityId):
    __tablename__ = "living_sfa_yu"
    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 1

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS}


class LivingArrangementSfaYa(SfaLivingBase, LivingArrangementId):
    __tablename__ = "living_sfa_ya"
    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 1

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "living_arrangement": [ALL]}


class LivingArrangementSfaYua(SfaLivingBase, UniversityId, LivingArrangementId):
    __tablename__ = "living_sfa_yua"
    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "living_arrangement": [ALL]}


class GradRateGrYu(GradRateBase, UniversityId):
    __tablename__ = "gradrate_gr_yu"

    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 1

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS}


class GradRateGrYur(GradRateBase, UniversityId, IPedsRaceId):
    __tablename__ = "gradrate_gr_yur"

    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "ipeds_race": [ALL]}


class GradRateGrYus(GradRateBase, UniversityId, SexId):
    __tablename__ = "gradrate_gr_yus"

    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "sex": [ALL]}


class GradRateGrYusr(GradRateBase, UniversityId, SexId, IPedsRaceId):
    __tablename__ = "gradrate_gr_yusr"

    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 3

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "sex": [ALL],
                "ipeds_race": [ALL]}


class UniversitySfaYu(BaseIpeds, UniversityId):
    __tablename__ = "university_sfa_yu"
    median_moe = 1

    year = db.Column(db.Integer(), primary_key=True)
    num_fed_loans = db.Column(db.Float)
    pct_fed_loans = db.Column(db.Float)
    pct_with_aid = db.Column(db.Float)
    total_fed_loans = db.Column(db.Float)
    avg_netprice_gos_aid = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS}


class AidSfaYui(BaseIpeds, UniversityId, IncomeRangeId):
    __tablename__ = "aid_sfa_yui"
    median_moe = 2

    year = db.Column(db.Integer(), primary_key=True)
    num_income = db.Column(db.Float)
    num_gos_award = db.Column(db.Float)
    avg_gos_award = db.Column(db.Float)
    avg_netprice_fedaid = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS,
                "income_range": [ALL]}


class FinancialsYu(FinancialsBase, UniversityId):
    __tablename__ = "financials_yu"

    year = db.Column(db.Integer(), primary_key=True)

    median_moe = 1

    @classmethod
    def get_supported_levels(cls):
        return {"year": [ALL],
                "university": UniversityId.LEVELS}
