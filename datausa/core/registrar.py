from datausa.pums.models import *
from datausa.ipeds.models import *
from datausa.onet.models import *
from datausa.chr.models import *
from datausa.bls.models import *
from datausa.cbp.models import *
from datausa.bea.models import *
from datausa.acs.models import *
from datausa.acs.automap_models import *

registered_models = [
    # PUMS
    Yg, Ygd, Ygr, Ygi, Ygio,
    Yo, Yow, Yos, Yod, Yor, Yoas,
    Ygo, Ygw, Ygor, Ygs, Ygb, Ygos,

    Yc, Ygc, Yca, Ycd, Ycb, Yoc, Yic, Ycs,
    Yi, Yio, Yior, Yios, Yocd, Yid, Yir, Yis,
    Yiw,
    Ya,

    # IPEDS
    TuitionYc, TuitionYcu, TuitionYcs, TuitionYgs,
    EnrollmentYcu,
    GradsYcu, GradsYc, GradsYcd,
    GradsYg, GradsYgc, GradsYgu, GradsYgs, GradsYgcd,
    GradsPctYcu,
    UnivGeo,

    # ONET
    SkillByCip, SkillBySoc,

    # County Health Rankings
    HealthYg,

    # Bureau of Labor Statistics
    OesYgo, QcewYgi, GrowthI, GrowthO,

    # County Business Patterns
    CbpYgi, CbpYg,

    # BEA I/O Tables
    BeaUse,

    # ACS 1-year
    Acs1_Ygl_Speakers,
    Acs1_Yg, Acs1_Yg_IncDist, Acs1_Yg_PovertyRace,
    Acs1_Yg_NatAge, Acs1_Yg_Race, Acs1_Yg_Conflict,
    Acs1_Yg_PropertyValue, Acs1_Yg_PropertyTax, Acs1_Yg_Vehicles,
    Acs1_Yg_TravelTime, Acs1_Yg_Transport,
    Acs1_Yg_Poverty, Acs1_Yg_Tenure, Acs1_Yg_Income,

    # ACS
    Acs5_Yg, Acs5_Yg_Income, Acs5_Yg_Conflict, Acs5_Yg_IncDist,
    Acs5_Ygo_Earnings,
    Acs5_Yg_NatAge, Acs5_Yg_Race, Acs5_Yg_Tenure, Acs5_Yg_Transport,
    Acs5_Yg_TravelTime, Acs5_Yg_Vehicles, Acs5_Yg_Poverty,
    Acs5_Yg_PropertyTax, Acs5_Yg_PropertyValue, Acs5_Ygl_Speakers,
    Acs5_Yg_PovertyRace,
    Acs5_Ygo_Num_Emp, Acs5_Ygi_Num_Emp,

    # ACS 3-year
    Acs3_Ygo_Num_Emp, Acs3_Ygi_Num_Emp, Acs3_Ygi_MedEarnings,


]


def register(cls):
    registered_models.append(cls)
