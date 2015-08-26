from datausa.pums.models import *
# from datausa.ipeds.models import *

registered_models = [
    # PUMS
    Yg, Ygd, Ygi, Ygio, Ygm, Ygmd, Ygo, Ygor, Ygos,
    # IPEDS
    # GradsYucd, Tuition, Enrollment,
    # GradsYgdState,
]

def register(cls):
    registered_models.append(cls)
