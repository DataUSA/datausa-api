from datausa.database import db
from datausa.attrs import consts
from datausa.attrs.models import University

from datausa.core.models import BaseModel
from datausa.attrs.consts import NATION, STATE, COUNTY, MSA, ALL
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData

metadata = MetaData(schema='chr')
AutomapBase = automap_base(bind=db.engine, metadata=metadata)


class HealthYg(AutomapBase, db.Model, BaseModel):
    __table_args__ = {"schema": "chr", "primary_key": ["geo_id"]}

    __tablename__ = 'yg'
    median_moe = 1

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": [ALL, STATE, COUNTY]}

AutomapBase.prepare(db.engine, reflect=True)
