from datausa.pums.abstract_models import *
from datausa.attrs.consts import ALL


class Ygi5(BasePums5, Employees, Year, GeoId, NaicsId, EmployeesRca):
    __tablename__ = "ygi"
    median_moe = 1.9

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "naics": NaicsId.LEVELS}


class Ygo5(BasePums5, Employees, Year, GeoId, SocId, EmployeesRca):
    __tablename__ = "ygo"
    median_moe = 1.9

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "soc": SocId.LEVELS}


class Yoas5(BasePums5, EmployeesWithAge, Year, SocId, SexId):
    __tablename__ = "yoas"
    median_moe = 2.9
    age = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"soc": SocId.LEVELS, "sex": [ALL], "age": [ALL]}


class Ygor5(BasePums5, Employees, Year, GeoId, SocId, RaceId):
    __tablename__ = "ygor"
    median_moe = 2.9

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "soc": SocId.LEVELS,
                "race": [ALL]}

class Ygos5(BasePums5, Employees, Year, GeoId, SocId, SexId):
    __tablename__ = "ygos"
    median_moe = 2.9

    @classmethod
    def get_supported_levels(cls):
        return {"geo": GeoId.LEVELS, "soc": SocId.LEVELS,
                "sex": [ALL]}
