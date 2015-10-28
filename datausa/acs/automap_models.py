from datausa.database import db

from datausa.acs.abstract_models import BaseAcs5, GeoId
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData

metadata = MetaData(schema='acs')
AutomapBase = automap_base(bind=db.engine, metadata=metadata)

class Acs5_Yg(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = "yg"
    median_moe = 1

class Acs5_Yg_IncDist(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = "yg_income_distribution"
    median_moe = 2

class Acs5_Yg_NatAge(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_nativity_age'
    median_moe = 1


class Acs5_Yg_Poverty(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_poverty'
    median_moe = 1


class Acs5_Yg_PropertyTax(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_property_tax'
    median_moe = 1


class Acs5_Yg_PropertyValue(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_property_value'
    median_moe = 1


class Acs5_Yg_Race(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_race'
    median_moe = 1


class Acs5_Yg_Tenure(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_tenure'
    median_moe = 1


class Acs5_Yg_Transport(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_transport'
    median_moe = 1


class Acs5_Yg_TravelTime(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_travel_time'
    median_moe = 1


class Acs5_Yg_Vehicles(AutomapBase, BaseAcs5, GeoId):
    __tablename__ = 'yg_vehicles'
    median_moe = 1

AutomapBase.prepare(db.engine, reflect=True)
