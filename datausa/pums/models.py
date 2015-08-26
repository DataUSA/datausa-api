from datausa.pums.abstract_models import *

class Yg(BasePums, Personal, Year, GeoId):
    __tablename__ = "yg"
    median_moe = 1

class Ygd(BasePums, Personal, Year, GeoId, DegreeId):
    __tablename__ = "ygd"
    median_moe = 2

class Ygi(BasePums, Personal, Year, GeoId, NaicsId):
    __tablename__ = "ygi"
    median_moe = 2

class Ygio(BasePums, Personal, Year, GeoId, NaicsId, SocId):
    __tablename__ = "ygio"
    median_moe = 3

class Ygm(BasePums, Personal, Year, GeoId, MajorId):
    __tablename__ = "ygm"
    median_moe = 2

class Ygmd(BasePums, Personal, Year, GeoId, MajorId, DegreeId):
    __tablename__ = "ygmd"
    median_moe = 3

class Ygo(BasePums, Personal, Year, GeoId, SocId):
    __tablename__ = "ygo"
    median_moe = 2

class Ygor(BasePums, Personal, Year, GeoId, RaceId):
    __tablename__ = "ygor"
    median_moe = 3

class Ygos(BasePums, Personal, Year, GeoId, SexId):
    __tablename__ = "ygos"
    median_moe = 3
