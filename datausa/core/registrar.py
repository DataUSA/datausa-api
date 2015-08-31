from datausa.pums.models import *
from datausa.ipeds.models import *

registered_models = [
    # PUMS
    Yg, Ygd, Ygi, Ygio,
    Ygo, Ygor, Ygos,
    # Ygc, Ygcd,
    Yca,

    # IPEDS
    TuitionYc, TuitionYcu,
    EnrollmentYcu,
    GradsYcu, GradsYgc,
]

def register(cls):
    registered_models.append(cls)
