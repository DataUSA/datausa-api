from datausa.database import db
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr
from datausa.attrs.consts import ALL
from datausa.attrs.models import Geo, University, UniversityCrosswalk
from sqlalchemy.orm import column_property
from sqlalchemy import func

class BaseEd(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "ed"}
    supported_levels = {"year": [ALL]}
    source_title = 'Official Cohort Default Rates for Schools'
    source_link = 'https://www2.ed.gov/offices/OSFAP/defaultmanagement/cdr.html'
    source_org = 'Department of Education'


class University(object):
    @declared_attr
    def opeid(cls):
        return db.Column(db.String(), primary_key=True)

    @declared_attr
    def university(cls):
        return column_property(UniversityCrosswalk.university)

    @classmethod
    def crosswalk_join(cls, qry):
        cond = UniversityCrosswalk.opeid == cls.opeid
        return qry.join(UniversityCrosswalk, cond)


class DefaultsYu(BaseEd, University):
    __tablename__ = "yu_defaults"
    median_moe = 1
    year = db.Column(db.Integer(), primary_key=True)
    opeid = db.Column(db.String(), primary_key=True)
    default_rate = db.Column(db.Float)
    num_defaults = db.Column(db.Integer)
    num_borrowers = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {
            "year": [ALL],
            "university": [ALL],
            "oped": [ALL]
        }
