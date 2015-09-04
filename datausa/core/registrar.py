from datausa.pums.models import *
from datausa.ipeds.models import *
from datausa.onet.models import *

registered_models = [
    # PUMS
    Yg, Ygd, Ygi, Ygio,
    Ygo, Ygor, Ygos,

    Yc, Ygc, Yca, Ycd, Ycb, Yoc, Yic,

    # IPEDS
    TuitionYc, TuitionYcu, TuitionYcs,
    EnrollmentYcu,
    GradsYcu, GradsYgc, GradsYc, GradsYcd,
    GradsPctYcu,

    #ONET
    SkillByCip,
]

def register(cls):
    registered_models.append(cls)

from datausa.onet.models import *