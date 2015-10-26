from datausa.pums.models import *
from datausa.ipeds.models import *
from datausa.onet.models import *
from datausa.chr.models import *
from datausa.bls.models import *
from datausa.cbp.models import *
from datausa.bea.models import *
from datausa.acs.models import *

registered_models = [
    # PUMS
    Yg, Ygd, Ygr, Ygi, Ygio,
    Yo, Yow,
    Ygo, Ygw, Ygor, Ygs, Ygos,

    Yc, Ygc, Yca, Ycd, Ycb, Yoc, Yic, Ycs,
    Yio, Yior, Yios, Yocd,

    # IPEDS
    TuitionYc, TuitionYcu, TuitionYcs,
    EnrollmentYcu,
    GradsYcu, GradsYgc, GradsYc, GradsYcd,
    GradsPctYcu,

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
    Acs5_Ygo_Num_Emp, Acs5_Ygo_Earnings,
]


def register(cls):
    registered_models.append(cls)
