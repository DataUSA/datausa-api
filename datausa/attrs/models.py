from datausa.database import db
from sqlalchemy import MetaData

class BaseAttr(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "attrs"}
    id = db.Column(db.String(10), primary_key=True)
    name =  db.Column(db.String())

    def serialize(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith("_")}

    def __repr__(self):
        return '<{}, id: {}, name: {}>'.format(self.__class__, self.id, self.name)

class University(BaseAttr):
    __tablename__ = 'university'

    state = db.Column(db.String)
    county = db.Column(db.String)
    msa = db.Column(db.String)

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    url = db.Column(db.String)

class Naics(BaseAttr):
    __tablename__ = 'naics'

class Soc(BaseAttr):
    __tablename__ = 'soc'
    level = db.Column(db.String)

class Cip(BaseAttr):
    __tablename__ = 'course'

class Degree(BaseAttr):
    __tablename__ = 'degree'

class Geo(BaseAttr):
    __tablename__ = 'geo_names'

    display_name = db.Column(db.String)
    sumlevel = db.Column(db.String)

class PumsDegree(BaseAttr):
    __tablename__ = 'degree'
    __table_args__ = {"schema": "pums_attrs"}

class PumsNaics(BaseAttr):
    __tablename__ = 'naics'
    __table_args__ = {"schema": "pums_attrs"}

class PumsSoc(BaseAttr):
    __tablename__ = 'soc'
    __table_args__ = {"schema": "pums_attrs"}

class PumsSex(BaseAttr):
    __tablename__ = 'sex'
    __table_args__ = {"schema": "pums_attrs"}

class PumsRace(BaseAttr):
    __tablename__ = 'race'
    __table_args__ = {"schema": "pums_attrs"}

class PumsBirthplace(BaseAttr):
    __tablename__ = 'birthplace'
    __table_args__ = {"schema": "pums_attrs"}

class Sector(BaseAttr):
    __tablename__ = 'sector'

class Skill(BaseAttr):
    __tablename__ = 'skill'

    avg_value = db.Column(db.Float)

class PumsNaicsCrosswalk(db.Model):
    __tablename__ = 'naics_crosswalk'
    __table_args__ = {"schema": "pums_attrs"}

    naics = db.Column(db.String, primary_key=True)
    pums_naics = db.Column(db.String)

    @classmethod
    def get_mapping(cls):
        all_objs = cls.query.all()
        return {obj.naics : obj.pums_naics for obj in all_objs}
