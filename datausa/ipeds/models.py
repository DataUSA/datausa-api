from datausa.ipeds.abstract_models import *

class Yc(Tuition, Cip):
    __tablename__ = "tuition_yc"
    median_moe = 1
    
    year = db.Column(db.Integer(), primary_key=True)
