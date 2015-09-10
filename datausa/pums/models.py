from datausa.pums.abstract_models import *

class Yc(BasePums, Personal, Year, CipId):
    __tablename__ = "yc"
    median_moe = 1

    avg_wage_rank = db.Column(db.Integer)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "all"]}

class Yca(BasePums, Personal, Year, CipId):
    __tablename__ = "yca"
    median_moe = 2

    age = db.Column(db.String(), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "all"]}

class Ycb(BasePums, Personal, Year, CipId, BirthplaceId):
    __tablename__ = "ycb"
    median_moe = 2

    num_ppl_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "all"], "birthplace": "all"} # TODO support in/out of US?

class Ycd(BasePums, Personal, Year, CipId, DegreeId):
    __tablename__ = "ycd"
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "all"], "degree": ["all"]}

class Yg(BasePums, Personal, Year, GeoId):
    __tablename__ = "yg"
    median_moe = 1

class Ygd(BasePums, Personal, Year, GeoId, DegreeId):
    __tablename__ = "ygd"
    median_moe = 2

class Ygi(BasePums, Personal, Year, GeoId, NaicsId):
    __tablename__ = "ygi"
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": GeoId.LEVELS, "naics": NaicsId.LEVELS}

class Ygio(BasePums, Personal, Year, GeoId, NaicsId, SocId):
    __tablename__ = "ygio"
    median_moe = 5
    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": GeoId.LEVELS,
                "soc": SocId.LEVELS,
                "naics": NaicsId.LEVELS}

# class Ygmd(BasePums, Personal, Year, GeoId, MajorId, DegreeId):
    # __tablename__ = "ygmd"
    # median_moe = 3

class Ygc(BasePums, Personal, Year, GeoId, CipId):
    __tablename__ = "ygc"
    median_moe = 2

    num_ppl_rca = db.Column(db.Float)

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": GeoId.LEVELS, "cip": ["2", "all"]}

class Ygo(BasePums, Personal, Year, GeoId, SocId):
    __tablename__ = "ygo"
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": GeoId.LEVELS, "soc": SocId.LEVELS}

class Ygor(BasePums, Personal, Year, GeoId, RaceId):
    __tablename__ = "ygor"
    median_moe = 3

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": GeoId.LEVELS, "soc": SocId.LEVELS,
                "race": ["all"]}

class Ygos(BasePums, Personal, Year, GeoId, SexId):
    __tablename__ = "ygos"
    median_moe = 3

    @classmethod
    def get_supported_levels(cls):
        return {"geo_id": GeoId.LEVELS, "soc": SocId.LEVELS,
                "sex": ["all"]}

class Yoc(BasePums, Personal, Year, SocId, CipId):
    __tablename__ = "yoc"
    median_moe = 2
    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "all"], "soc": SocId.LEVELS}

class Yic(BasePums, Personal, Year, NaicsId, CipId):
    __tablename__ = "yic"
    median_moe = 2
    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2"], "naics": NaicsId.LEVELS}

class Yio(BasePums, Personal, Year, NaicsId, SocId):
    __tablename__ = "yio"
    median_moe = 2

    @classmethod
    def get_supported_levels(cls):
        return {"soc": SocId.LEVELS, "naics": NaicsId.LEVELS}

class Yior(BasePums, Personal, Year, NaicsId, SocId, RaceId):
    __tablename__ = "yior"
    median_moe = 3

    @classmethod
    def get_supported_levels(cls):
        return {"soc": SocId.LEVELS, "naics": NaicsId.LEVELS, "race": ["all"]}

class Yios(BasePums, Personal, Year, NaicsId, SocId, SexId):
    __tablename__ = "yios"
    median_moe = 3

    @classmethod
    def get_supported_levels(cls):
        return {"soc": SocId.LEVELS, "naics": NaicsId.LEVELS, "sex": ["all"]}

class Yocd(BasePums, Personal, Year, SocId, CipId, DegreeId):
    __tablename__ = "yocd"
    median_moe = 3

    @classmethod
    def get_supported_levels(cls):
        return {"cip": ["2", "all"], "soc": SocId.LEVELS, "degree": ["all"]}
