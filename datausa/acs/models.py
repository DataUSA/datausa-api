from datausa.acs.abstract_models import BaseAcs5, GeoId
from datausa.acs.abstract_models import db


class Acs5_Yg(BaseAcs5, GeoId):
    __tablename__ = "yg"
    median_moe = 1

    year = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Float)
    age_moe = db.Column(db.Float)
    age_rank = db.Column(db.Integer)
    pop = db.Column(db.Float)
    pop_moe = db.Column(db.Float)
    pop_rank = db.Column(db.Integer)
    income = db.Column(db.Float)
    income_moe = db.Column(db.Float)
    income_rank = db.Column(db.Integer)
