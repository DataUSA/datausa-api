from datausa.pums.models import *
from datausa.ipeds.models import *

registered_models = [
    # PUMS
    Yg, Ygd, Ygi, Ygio,
    Ygo, Ygor, Ygos,
    # Ygc, Ygcd,
    Yca, Ycd, Ycb, Yoc, Yic,

    # IPEDS
    TuitionYc, TuitionYcu, TuitionYcs,
    EnrollmentYcu,
    GradsYcu, GradsYgc, GradsYc, GradsYcd,
    GradsPctYcu,
]

def register(cls):
    registered_models.append(cls)
