from datausa.database import db
from sqlalchemy import MetaData

class BaseAttr(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "attrs"}
    id = db.Column(db.String(10), primary_key=True)
    name =  db.Column(db.String())

    def serialize(self):
        return {
            "id": self.id,
            "name" : self.name
        }

    def __repr__(self):
        return '<{}, id: {}, name: {}>'.format(self.__class__, self.id, self.name)

class University(BaseAttr):
    __tablename__ = 'university'

    state = db.Column(db.String)
    county = db.Column(db.String)
    msa = db.Column(db.String)

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

class Naics(BaseAttr):
    __tablename__ = 'naics'

class Soc(BaseAttr):
    __tablename__ = 'soc'
    level = db.Column(db.String)

class Course(BaseAttr):
    __tablename__ = 'course'

class Degree(BaseAttr):
    __tablename__ = 'degree'