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
    Yo, Yow,
    Ygo, Ygw, Ygor, Ygs, Ygos,

    Yc, Ygc, Yca, Ycd, Ycb, Yoc, Yic, Ycs,
    Yio, Yior, Yios, Yocd,

    # IPEDS
    TuitionYc, TuitionYcu, TuitionYcs, TuitionYgs,
    EnrollmentYcu,
    GradsYcu, GradsYc, GradsYcd,
    GradsYgc, GradsYgu, GradsYgs, GradsYgcd,
    GradsPctYcu,
    UnivGeo,

    # ONET
    SkillByCip,

    # County Health Rankings
    HealthYg,

    # Bureau of Labor Statistics
    OesYgo, QcewYgi,

    # County Business Patterns
    CbpYgi, CbpYg,

    # BEA I/O Tables
    BeaUse,

    # ACS
    Acs5_Yg, Acs5_Yg_Income, Acs5_Yg_Conflict, Acs5_Yg_IncDist,
    Acs5_Ygo_Earnings,
    Acs5_Yg_NatAge, Acs5_Yg_Race, Acs5_Yg_Tenure, Acs5_Yg_Transport,
    Acs5_Yg_TravelTime, Acs5_Yg_Vehicles, Acs5_Yg_Poverty,
    Acs5_Yg_PropertyTax, Acs5_Yg_PropertyValue, Acs5_Ygl_Speakers,
    Acs5_Yg_PovertyRace,

    # ACS 3-year
    Acs3_Ygo_Num_Emp, Acs3_Ygi_Num_Emp,
]


def register(cls):
    registered_models.append(cls)
