from datausa.database import db
from sqlalchemy import MetaData

class BaseGrads(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "ipeds"}
    total = db.Column(db.Integer())
    total_men =  db.Column(db.Integer())
    total_women =  db.Column(db.Integer())

class GradsYucd(BaseGrads):
    __tablename__ = "grads_yucd"
    year = db.Column(db.String(), primary_key=True)
    university_id = db.Column(db.String(), primary_key=True)
    course_id = db.Column(db.String(), primary_key=True)
    degree_id = db.Column(db.String(), primary_key=True)

    def __repr__(self):
        return '<{}>'.format(self.__class__)