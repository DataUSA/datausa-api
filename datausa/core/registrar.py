from datausa.pums.models import *
from datausa.pums.models_5 import *
from datausa.ipeds.models import *
from datausa.onet.models import *
from datausa.chr.models import *
from datausa.bls.models import *
from datausa.cbp.models import *
from datausa.bea.models import *
from datausa.acs.models import *
from datausa.acs.automap_models import *
from datausa.acs.stats_models import *
from datausa.dartmouth.models import *
from datausa.freight.models import *
from datausa.ed.models import DefaultsYg, DefaultsYu, DefaultsYur, DefaultsYure
from datausa.attrs.models import UniversityCrosswalk
from datausa.opiods.models import DrugOverdoseDeathRate, OpiodOverdoseDeathRate, NonMedUsePainMeds

registered_models = [
    # PUMS
    Yg, Ygd, Ygr, Ygi, Ygio,
    Yo, Yow, Yos, Yod, Yor, Yoas,
    Ygo, Ygw, Ygor, Ygs, Ygb, Ygos,

    Yc, Ygc, Yca, Ycd, Ycb, Yoc, Yic, Ycs,
    Yi, Yio, Yior, Yios, Yocd, Yid, Yir, Yis,
    Yiw,
    Ya,

    # PUMS 5-year tables
    Ygo5, Ygi5, Yoas5, Ygor5, Ygos5, Ygb5,

    # IPEDS
    TuitionYu, TuitionYc, TuitionYcu, TuitionYcs, TuitionYgs,
    GradsYu, GradsYcu, GradsYc, GradsYcd, GradsYgd, GradsYud, GradsYucd,
    GradsYg, GradsYgc, GradsYgu, GradsYgs, GradsYgcd,
    GradsPctYcu,
    UnivGeo,
    AdmissionsY,
    AdmissionsYu,
    EnrollmentEfaYusrle,
    EnrollmentEfaYusrle,
    EnrollmentEfaYus,
    EnrollmentEfaYue,
    EnrollmentEfaYul,
    EnrollmentEfaYur,
    LivingArrangementSfaYa, LivingArrangementSfaYu, LivingArrangementSfaYua,
    GradRateGrYu, GradRateGrYur, GradRateGrYus, GradRateGrYusr,
    FinancialsYu,
    AidSfaYui, UniversitySfaYu,
    FinancialsEndowmentQuintilesYu,
    RetentionEfdYu,
    NISSalariesYu,
    NISSalariesYuo,
    ISSalariesYu,
    ISSalariesYua,
    ISSalariesYus,
    ISSalariesYuas,
    ExpensesYu,
    ExpensesYue,
    ICLivingExpensesYua, ICMaxLivingExpensesYua,
    GradRateTimeframeYut,
    # ONET
    SkillByCip, SkillBySoc,

    # Dartmouth
    YgPrimaryCare, YgReimbursements, YgcPostDischarge,

    # County Health Rankings
    HealthYg,

    # Bureau of Labor Statistics
    OesYgo, QcewYgi, GrowthI16, GrowthI, GrowthO16, GrowthO, CesYi,

    # County Business Patterns
    CbpYgi, CbpYg,

    # BEA I/O Tables
    BeaUse,

    # ACS 1-year
    Acs1_Ygl_Speakers,
    Acs1_Ygo_Num_Emp, Acs1_Ygo_Earnings, Acs1_Ygi_Num_Emp,
    Acs1_Yg, Acs1_Yg_IncDist, Acs1_Yg_PovertyRace,
    Acs1_Yg_NatAge, Acs1_Yg_Race, Acs1_Yg_Conflict,
    Acs1_Yg_PropertyValue, Acs1_Yg_PropertyTax, Acs1_Yg_Vehicles,
    Acs1_Yg_TravelTime, Acs1_Yg_Transport,
    Acs1_Yg_Poverty, Acs1_Yg_Tenure, Acs1_Yg_Income,
    Acs1_Yg_Num_Emp,
    # ACS
    Acs5_Yg, Acs5_Yg_Income, Acs5_Yg_Conflict, Acs5_Yg_IncDist,
    Acs5_Ygo_Earnings,
    Acs5_Yg_NatAge, Acs5_Yg_Race, Acs5_Yg_Tenure, Acs5_Yg_Transport,
    Acs5_Yg_TravelTime, Acs5_Yg_Vehicles, Acs5_Yg_Poverty,
    Acs5_Yg_PropertyTax, Acs5_Yg_PropertyValue, Acs5_Ygl_Speakers,
    Acs5_Yg_PovertyRace,
    Acs5_Ygo_Num_Emp, Acs5_Ygi_Num_Emp,
    Acs5_Yg_Num_Emp,
    # ACS 3-year
    Acs3_Ygo_Num_Emp, Acs3_Ygi_Num_Emp, Acs3_Ygi_MedEarnings,

    # Stats
    StateStats, CountyStats, MSAStats, PlaceStats, PUMAStats,

    # ACS Health
    Acs1_Yga_Health, Acs1_Ygai_Health, Acs1_Ygais_Health,
    Acs1_Ygas_Health, Acs1_Ygi_Health, Acs1_Ygis_Health, Acs1_Ygs_Health,

    # Freight
    FAFYodmp, FAFYodp, FAFYomp, FAFYodm, FAFYop, FAFYdp, FAFYdm, FAFYom, FAFYod,

    # Loans
    DefaultsYu, DefaultsYg, DefaultsYur, DefaultsYure, UniversityCrosswalk,

    # Opiods
    DrugOverdoseDeathRate, OpiodOverdoseDeathRate, NonMedUsePainMeds
]


def register(cls):
    registered_models.append(cls)
