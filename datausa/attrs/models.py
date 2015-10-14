from datausa.database import db
from sqlalchemy.orm import relationship

class BaseAttr(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "attrs"}
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String())
    HEADERS = ["id", "name"]

    @classmethod
    def parents(cls, attr_id):
        raise Exception("Not implemented!")

    @classmethod
    def children(cls, attr_id):
        raise Exception("Not implemented!")

    def serialize(self):
        return {key: val for key, val in self.__dict__.items()
                if not key.startswith("_")}

    def data_serialize(self):
        return [self.id, self.name]

    def __repr__(self):
        return '<{}, id: {}, name: {}>'.format(self.__class__,
                                               self.id, self.name)


class University(BaseAttr):
    __tablename__ = 'university'

    state = db.Column(db.String)
    county = db.Column(db.String)
    msa = db.Column(db.String)
    sector = db.Column(db.Integer)

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    url = db.Column(db.String)


class Naics(BaseAttr):
    __tablename__ = 'naics'

    @classmethod
    def parents(cls, naics_id):
        mylen = len(naics_id)
        if mylen > 2 and "-" not in naics_id:
            ids = [naics_id[:naics_len] for naics_len in range(2, mylen)]
            if ids[0][:2] in ["31", "32", "33"]:
                ids[0] = "31-33"
            elif ids[0][:2] in ["44", "45"]:
                ids[0] = "44-45"
        naics = Naics.query.filter(Naics.id.in_(ids)).all()
        return [attr.data_serialize() for attr in naics], Naics.HEADERS

    @classmethod
    def children(cls, naics_id):
        naics_map = {"31-33": ["31", "32", "33"], "44-45": ["44", "45"]}
        targets = naics_map[naics_id] if naics_id in naics_map else [naics_id]
        filters = [Naics.id.startswith(target) for target in targets]
        filters.append(Naics.id != naics_id)
        naics = Naics.query.filter(*filters).distinct(Naics.id).all()
        return [attr.data_serialize() for attr in naics], Naics.HEADERS


class Soc(BaseAttr):
    __tablename__ = 'soc'
    level = db.Column(db.String)

    @classmethod
    def parents(cls, soc_id):
        broad = soc_id[:-1] + '0'
        minor_1 = soc_id[:3] + '000'
        minor_2 = soc_id[:3] + '100'
        major = soc_id[:2] + '0000'

        myparents = [major, minor_1, minor_2, broad]

        socs = Soc.query.filter(Soc.id.in_(myparents)).all()
        return [[attr.id, attr.name] for attr in socs], ["id", "name"]


class Cip(BaseAttr):
    __tablename__ = 'course'

    @classmethod
    def parents(cls, cip_id):
        cips = []
        if len(cip_id) >= 4:
            cips.append(cip_id[:2])
        if len(cip_id) == 6:
            cips.append(cip_id[:4])
        cips = Cip.query.filter(Cip.id.in_(cips)).all()
        return [[attr.id, attr.name] for attr in cips], ["id", "name"]


class Degree(BaseAttr):
    __tablename__ = 'degree'


class Geo(BaseAttr):
    __tablename__ = 'geo_names'

    display_name = db.Column(db.String)
    sumlevel = db.Column(db.String)

    @classmethod
    def parents(cls, geo):
        mysumlevel = geo[:3]
        geos = GeoContainment.query.filter(GeoContainment.child_geoid == geo).order_by("percent_covered asc").all()
        levels = [[gobj.parent.id, gobj.parent.name] for gobj in geos]

        if mysumlevel in ['050', '140', '795']:
            state_id = "04000US" + geo.split("US")[1][:2]
            state = Geo.query.filter_by(id=state_id).one()
            levels.insert(0, [state_id, state.name])
        if mysumlevel != '010':
            levels.insert(0, ["01000US", "United States"])
        return levels, ["id", "name"]


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


class PumsWage(BaseAttr):
    __tablename__ = 'wage_bin'
    __table_args__ = {"schema": "pums_attrs"}


class PumsBirthplace(BaseAttr):
    __tablename__ = 'birthplace'
    __table_args__ = {"schema": "pums_attrs"}


class Sector(BaseAttr):
    __tablename__ = 'sector'
    color = db.Column(db.String)


class Skill(BaseAttr):
    __tablename__ = 'skill'

    avg_value = db.Column(db.Float)


class PumsNaicsCrosswalk(db.Model):
    __tablename__ = 'naics_crosswalk'
    __table_args__ = {"schema": "pums_attrs"}

    naics = db.Column(db.String, primary_key=True)
    pums_naics = db.Column(db.String)


class IoCode(BaseAttr):
    __tablename__ = 'iocode'


class IoCodeCrosswalk(db.Model):
    __tablename__ = 'iocode_crosswalk'
    __table_args__ = {"schema": "attrs"}

    naics = db.Column(db.String, db.ForeignKey(Naics.id), primary_key=True)
    iocode = db.Column(db.String, db.ForeignKey(IoCode.id), primary_key=True)
    iocode_parent = db.Column(db.String, db.ForeignKey(IoCode.id))


class GeoContainment(db.Model):
    __tablename__ = 'geo_containment'
    __table_args__ = {"schema": "attrs"}
    child_geoid = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    parent_geoid = db.Column(db.String, db.ForeignKey(Geo.id),
                             primary_key=True)
    percent_covered = db.Column(db.Float)
    parent = relationship('Geo', foreign_keys='GeoContainment.parent_geoid')
