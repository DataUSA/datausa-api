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
    __table_args__ = {"schema": "chr"}
    source_title = 'University of Wisconsin County Health Rankings'
    __tablename__ = 'yg'
    median_moe = 1

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": [ALL, STATE, COUNTY]}

    @classmethod
    def geo_id_filter(cls, level):
        if level == ALL:
            return True
        level_map = {STATE: "040", COUNTY: "050"}
        level_code = level_map[level]
        return cls.geo_id.startswith(level_code)

AutomapBase.prepare(db.engine, reflect=True)
