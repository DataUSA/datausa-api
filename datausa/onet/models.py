from datausa.database import db
from datausa.attrs.models import Skill
from datausa.ipeds.abstract_models import CipId
from datausa.core.models import BaseModel
from sqlalchemy.ext.declarative import declared_attr

class BaseOnet(db.Model, BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "onet"}
    supported_levels = {}
    source_title = 'O*NET'
    source_link = 'http://www.onetonline.org/'
    source_org = 'Department of Labor'

class SkillId(object):
    @declared_attr
    def skill(cls):
        return db.Column(db.String(), db.ForeignKey(Skill.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6"]}

class SkillByCip(BaseOnet, SkillId, CipId):
    __tablename__ = "skills_by_cip"
    median_moe = 1

    value = db.Column(db.Float)
    value_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "4", "6", "all"], "skill": ["all"]}

class SkillBySoc(BaseOnet, SkillId):
    __tablename__ = "skills_by_soc"
    median_moe = 1

    soc = db.Column(db.String(), primary_key=True)
    value = db.Column(db.Float)
    value_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"soc": ["all"], "skill": ["all"]}
