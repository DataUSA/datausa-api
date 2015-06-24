from datausa.pums.models import *
from datausa.ipeds.models import *

registered_models = [
    # PUMS
    StateYeg, NationYeg, 
    NationYegPTax, StateYegPTax, PumaYegPTax,
    # IPEDS
    GradsYucd, Tuition, Enrollment
]
