from datausa.database import db
from datausa.attrs import consts
from datausa.attrs.models import University, Course
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
from sqlalchemy import select, func
from datausa.core.models import BaseModel

class BaseIpeds(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "ipeds"}


class BaseGrads(BaseIpeds):
    __abstract__ = True
    total = db.Column(db.Integer())
    total_men =  db.Column(db.Integer())
    total_women =  db.Column(db.Integer())

class GradsYucd(BaseGrads):
    __tablename__ = "grads_yucd"
    year = db.Column(db.String(), primary_key=True)
    university_id = db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)
    course_id = db.Column(db.String(), db.ForeignKey(Course.id), primary_key=True)
    degree_id = db.Column(db.String(), primary_key=True)
    course_id_len = db.Column(db.Integer())

    geo_id = column_property(select([University.state]).where(University.id == university_id).label('geo_id'))
    supported_levels = {
        "geo_id" : [consts.STATE],
        "university_id" : "all"
    }

    def __repr__(self):
        return '<{}>'.format(self.__class__)

class Enrollment(BaseIpeds):
    __tablename__ = "enrollment_yu"
    year = db.Column(db.String(), primary_key=True)
    university_id = db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)
    
    total = db.Column(db.Integer())
    men =  db.Column(db.Integer())
    women =  db.Column(db.Integer())
    black =  db.Column(db.Integer())
    asian =  db.Column(db.Integer())
    native =  db.Column(db.Integer())
    unknown =  db.Column(db.Integer())
    
    supported_levels = {
        "university_id": "all"
    }



class Tuition(BaseIpeds):
    __tablename__ = "tuition_yu"
    year = db.Column(db.String(), primary_key=True)
    university_id = db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)
    
    oos_tuition = db.Column(db.Integer())
    state_tuition = db.Column(db.Integer())
    district_tuition = db.Column(db.Integer())

    oos_fee = db.Column(db.Integer())
    state_fee = db.Column(db.Integer())
    district_fee = db.Column(db.Integer())
    
    supported_levels = {
        "university_id": "all"
    }