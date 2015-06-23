from datausa.database import db
from datausa.attrs import consts
from datausa.attrs.models import University, Course
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
from sqlalchemy import select, func


class BaseGrads(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "ipeds"}
    total = db.Column(db.Integer())
    total_men =  db.Column(db.Integer())
    total_women =  db.Column(db.Integer())

class GradsYucd(BaseGrads):
    __tablename__ = "grads_yucd"
    year = db.Column(db.String(), primary_key=True)
    university_id = db.Column(db.String(), db.ForeignKey(University.id), primary_key=True)
    course_id = db.Column(db.String(), db.ForeignKey(Course.id), primary_key=True)
    degree_id = db.Column(db.String(), primary_key=True)

    geo_id = column_property(select([University.state]).where(University.id == university_id).label('geo_id'))
    supported_levels = {
        "geo_id" : [consts.STATE],
        "university_id" : "all"
    }

    def __repr__(self):
        return '<{}>'.format(self.__class__)