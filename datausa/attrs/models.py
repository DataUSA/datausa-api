from datausa.database import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import or_, asc
from sqlalchemy.sql import text
from datausa.attrs.consts import ALL
from datausa.core.models import BaseModel


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


class ImageAttr(db.Model):
    __abstract__ = True
    image_link = db.Column(db.String)
    image_author = db.Column(db.String)
    url_name = db.Column(db.String)
    image_meta = db.Column(db.String)
    keywords = db.Column(db.ARRAY(db.String))

    HEADERS = ["id", "name", "image_link", "image_author", "url_name", "image_meta", "keywords"]

    def data_serialize(self):
        return [self.id, self.name, self.image_link, self.image_author, self.url_name, self.image_meta]


class University(BaseAttr, ImageAttr):
    __tablename__ = 'university'

    state = db.Column(db.String)
    county = db.Column(db.String)
    msa = db.Column(db.String)
    sector = db.Column(db.String)
    opeid8 = db.Column(db.String)
    status = db.Column(db.String)
    carnegie = db.Column(db.String)
    carnegie_parent = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    url = db.Column(db.String)
    is_stem = db.Column(db.Integer)


class Naics(BaseAttr):
    __tablename__ = 'bls_naics'
    level = db.Column(db.Integer)

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
    def children(cls, naics_id, **kwargs):
        target_level = len(naics_id) + 1
        naics_map = {"31-33": ["31", "32", "33"], "44-45": ["44", "45"]}
        targets = [naics_id]
        if naics_id in naics_map:
            target_level = 3
            targets = naics_map[naics_id]
        filters = [Naics.id.startswith(target) for target in targets]
        filters.append(Naics.id != naics_id)
        show_all = kwargs.get("show_all", False)
        if not show_all:
            filters.append(func.length(Naics.id) == target_level)
        naics = Naics.query.filter(*filters).distinct(Naics.id).all()
        return [attr.data_serialize() for attr in naics], Naics.HEADERS


class Soc(BaseAttr):
    __tablename__ = 'bls_soc'
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

    @classmethod
    def children(cls, soc_id, **kwargs):
        # find the prefix Soc ID
        if len(soc_id) != 6:
            raise Exception("Invalid SOC id")

        show_all = kwargs.get("show_all", False)
        prefix = soc_id.rstrip("0").rstrip("Y").rstrip("X")
        transition_map = {"major": "minor", "minor": "broad",
                          "broad": "detailed", "detailed": "none"}
        level = Soc.query.filter(Soc.id == soc_id).one().level
        next_level = transition_map[level]
        # # find IDs starting with this prefix not equal to this prefix
        filters = [Soc.id.startswith(prefix), Soc.id != soc_id]
        if not show_all:
            filters.append(Soc.level == next_level)
        socs = Soc.query.filter(*filters).distinct(Soc.id).all()
        return [attr.data_serialize() for attr in socs], Soc.HEADERS


class Cip(BaseAttr, ImageAttr):
    __tablename__ = 'course'
    level = db.Column(db.Integer)
    name_long = db.Column(db.String)
    is_stem = db.Column(db.Boolean)

    @classmethod
    def parents(cls, cip_id, **kwargs):
        show_all = kwargs.get("show_all", True)
        cips = []
        if len(cip_id) >= 4:
            cips.append(cip_id[:2])
        if len(cip_id) == 6:
            cips.append(cip_id[:4])
        if not show_all:
            cips = [cips[-1]]
        cips = Cip.query.filter(Cip.id.in_(cips)).order_by(asc(func.length(Cip.id))).all()
        return [attr.data_serialize() for attr in cips], Cip.HEADERS

    @classmethod
    def children(cls, cip_id, **kwargs):
        show_all = kwargs.get("show_all", False)
        sumlevel = kwargs.get("sumlevel", False)

        filters = [Cip.id.startswith(cip_id), Cip.id != cip_id]
        if not show_all:
            # if we are not showing all children, then only display
            # cip attrs of length (parent length) + 2
            t_map = {0: 2, 1: 4, 2: 6}
            target = len(cip_id) + 2
            if sumlevel:
                target = t_map[int(sumlevel[0])]
            filters.append(func.length(Cip.id) == target)
        cips = Cip.query.filter(*filters).distinct(Cip.id).all()
        return [attr.data_serialize() for attr in cips], Cip.HEADERS


class Cohort(BaseAttr):
    __tablename__ = 'cohort'


class Degree(BaseAttr):
    __tablename__ = 'degree'


class Geo(BaseAttr, ImageAttr):
    __tablename__ = 'geo_names'

    display_name = db.Column(db.String)
    name_long = db.Column(db.String)
    sumlevel = db.Column(db.String)
    HEADERS = ["id", "name", "url_name"]

    @classmethod
    def parents(cls, geo):
        mysumlevel = geo[:3]
        filters = [GeoContainment.child_geoid == geo]
        geos = GeoContainment.query.filter(*filters).order_by(text("percent_covered asc")).all()
        geos2 = []
        for g in geos:
            if g.parent_geoid.startswith("795"):
                if g.percent_covered >= 100:
                    geos2.append(g)
            else:
                geos2.append(g)
        levels = [[gobj.parent.id, gobj.parent.name, gobj.parent.url_name] for gobj in geos2]
        if mysumlevel in ['050', '140', '795', '160']:
            state_id = "04000US" + geo.split("US")[1][:2]
            state = Geo.query.filter_by(id=state_id).one()
            levels.insert(0, [state_id, state.name, state.url_name])
        if mysumlevel != '010':
            levels.insert(0, ["01000US", "United States", "united-states"])
        return levels, Geo.HEADERS

    @classmethod
    def children(cls, geo, **kwargs):
        simple_levels = {
            '010': ['040'],
            '040': ['050', '060', '101', '140', '160', '795'],
            '050': ['140'],
        }
        defaults = {'010': '040',
                    '040': '050',
                    '050': '140',
                    '160': '140',
                    '310': '140,160'}
        sumlevel = geo[:3]
        if 'sumlevel' not in kwargs:
            child_level = defaults[sumlevel]
        else:
            child_level = kwargs['sumlevel'][0]
        if sumlevel in simple_levels and child_level in simple_levels[sumlevel]:
            child_prefix = '{}00US{}'.format(child_level, geo.split('US')[1])
            filters = [Geo.id.startswith(child_prefix)]
            geos = Geo.query.filter(*filters).all()
            levels = [[gobj.id, gobj.name] for gobj in geos]
        else:
            filters = [GeoContainment.parent_geoid == geo]
            child_level = child_level.split(",") if isinstance(child_level, basestring) else child_level
            lvls = [GeoContainment.child_geoid.startswith(lvl) for lvl in child_level]
            filters.append(or_(*lvls))
            geos = GeoContainment.query.filter(*filters).all()
            levels = [[gobj.child.id, gobj.child.name] for gobj in geos]

        return levels, Geo.HEADERS


class PumsDegree(BaseAttr):
    __tablename__ = 'degree'
    __table_args__ = {"schema": "pums_attrs"}


class PumsNaics(BaseAttr, ImageAttr):
    __tablename__ = 'pums_naics'
    __table_args__ = {"schema": "pums_attrs"}
    id = db.Column(db.String(10), primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.String, db.ForeignKey(id))
    grandparent = db.Column(db.String, db.ForeignKey(id))

    @classmethod
    def children(cls, naics_id, **kwargs):
        objs = PumsNaics.query.filter(PumsNaics.parent == naics_id)
        data = [[obj.id, obj.name] for obj in objs if obj.id != naics_id]
        return data, PumsNaics.HEADERS

    @classmethod
    def parents(cls, naics_id, **kwargs):
        naics_obj = PumsNaics.query.filter_by(id=naics_id).first()
        tmp = []
        if naics_obj and naics_obj.grandparent:
            tmp.append(PumsNaics.query.filter_by(id=naics_obj.grandparent).first())
        if naics_obj and naics_obj.parent:
            tmp.append(PumsNaics.query.filter_by(id=naics_obj.parent).first())
        tmp = [[x.id, x.name] for x in tmp if x]
        return tmp, PumsNaics.HEADERS


class PumsSoc(BaseAttr, ImageAttr):
    __tablename__ = 'pums_soc'
    __table_args__ = {"schema": "pums_attrs"}
    id = db.Column(db.String(10), primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.String)
    grandparent = db.Column(db.String)
    great_grandparent = db.Column(db.String)

    @classmethod
    def parents(cls, soc_id, **kwargs):
        soc_hobj = SocHierarchy.query.filter_by(soc=soc_id).first()
        parents = [soc_hobj.great_grandparent_obj, soc_hobj.grandparent_obj, soc_hobj.parent_obj]
        data = [[p.id, p.name] for p in parents if p]
        return data, PumsNaics.HEADERS

    @classmethod
    def children(cls, soc_id, **kwargs):
        objs = SocHierarchy.query.filter_by(parent=soc_id).all()
        data = [[obj.soc_obj.id, obj.soc_obj.name] for obj in objs]
        return data, PumsSoc.HEADERS


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

    adm0_a3 = db.Column(db.String)
    demonym = db.Column(db.String)


class Sector(BaseAttr):
    __tablename__ = 'sector'
    color = db.Column(db.String)


class Race(BaseAttr):
    __tablename__ = 'race'


class Skill(BaseAttr):
    __tablename__ = 'skill'

    avg_value = db.Column(db.Float)
    parent = db.Column(db.String)


class IPedsToPumsCrosswalk(db.Model):
    __tablename__ = 'ipeds_to_pums_soc'
    __table_args__ = {"schema": "attrs"}

    ipeds_occ = db.Column(db.String, primary_key=True)
    pums_soc = db.Column(db.String, primary_key=True)


class PumsNaicsCrosswalk(db.Model):
    __tablename__ = 'naics_crosswalk'
    __table_args__ = {"schema": "pums_attrs"}

    naics = db.Column(db.String, primary_key=True)
    pums_naics = db.Column(db.String)


class PumsIoCrosswalk(db.Model):
    __tablename__ = 'naics_to_io'
    __table_args__ = {"schema": "pums_attrs"}

    pums_naics = db.Column(db.String, primary_key=True)
    iocode = db.Column(db.String)
    iocode_parent = db.Column(db.String)


class IoCode(BaseAttr):
    __tablename__ = 'iocode'
    HEADERS = ["id", "name", "level", "parent"]

    level = db.Column(db.Integer)
    parent = db.Column(db.String)


class GeoCrosswalker(db.Model):
    __tablename__ = 'geo_crosswalker'
    __table_args__ = {"schema": "attrs"}
    geo_a = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    geo_b = db.Column(db.String, db.ForeignKey(Geo.id),
                      primary_key=True)
    a = relationship('Geo', foreign_keys='GeoCrosswalker.geo_a')
    b = relationship('Geo', foreign_keys='GeoCrosswalker.geo_b', lazy='subquery')


class GeoContainment(db.Model):
    __tablename__ = 'geo_containment'
    __table_args__ = {"schema": "attrs"}
    child_geoid = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    parent_geoid = db.Column(db.String, db.ForeignKey(Geo.id),
                             primary_key=True)
    area_covered = db.Column(db.Float)
    percent_covered = db.Column(db.Float)
    parent = relationship('Geo', foreign_keys='GeoContainment.parent_geoid')
    child = relationship('Geo', foreign_keys='GeoContainment.child_geoid',
                         lazy='subquery')


class GeoNeighbors(db.Model):
    __tablename__ = 'geo_neighbors'
    __table_args__ = {"schema": "attrs"}
    geo = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    neighbor = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)


class AcsOcc(BaseAttr):
    __tablename__ = 'acs_occ'
    level = db.Column(db.Integer)


class AcsInd(BaseAttr):
    __tablename__ = 'acs_ind'
    level = db.Column(db.Integer)


class SocHierarchy(db.Model):
    __tablename__ = 'pums_soc_hierarchy'
    __table_args__ = {"schema": "hierarchies"}
    great_grandparent = db.Column(db.String, db.ForeignKey(PumsSoc.id))
    grandparent = db.Column(db.String, db.ForeignKey(PumsSoc.id))
    parent = db.Column(db.String, db.ForeignKey(PumsSoc.id))
    soc = db.Column(db.String, db.ForeignKey(PumsSoc.id), primary_key=True)
    parent_obj = relationship('PumsSoc', foreign_keys='SocHierarchy.parent', lazy='subquery')
    grandparent_obj = relationship('PumsSoc', foreign_keys='SocHierarchy.grandparent', lazy='subquery')
    great_grandparent_obj = relationship('PumsSoc', foreign_keys='SocHierarchy.great_grandparent', lazy='subquery')
    soc_obj = relationship('PumsSoc', foreign_keys='SocHierarchy.soc', lazy='subquery')


class AgeBucket(BaseAttr):
    __tablename__ = 'age_bucket'


class Insurance(BaseAttr):
    __tablename__ = 'insurance'


class AcsLanguage(BaseAttr):
    __tablename__ = 'language'


class AcsRace(BaseAttr):
    __tablename__ = 'acs_race'


class Conflict(BaseAttr):
    __tablename__ = 'conflict'


class Sctg(BaseAttr):
    __tablename__ = 'sctg'
    parent = db.Column(db.String)


class Napcs(BaseAttr):
    __tablename__ = 'napcs'


class Search(BaseAttr):
    __tablename__ = 'search_v8'
    id = db.Column(db.String, primary_key=True)
    zvalue = db.Column(db.Float)
    kind = db.Column(db.String, primary_key=True)
    display = db.Column(db.String)
    sumlevel = db.Column(db.String, primary_key=True)
    is_stem = db.Column(db.Boolean)
    url_name = db.Column(db.String)
    keywords = db.Column(db.ARRAY(db.String))


class ZipLookup(db.Model):
    __tablename__ = 'zip_lookup'
    __table_args__ = {"schema": "attrs"}
    child_geoid = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    parent_geoid = db.Column(db.String, db.ForeignKey(Search.id),
                             primary_key=True)
    percent_covered = db.Column(db.Float)
    parent_area = db.Column(db.Float)


class OccCrosswalk(db.Model):
    __tablename__ = 'occ_crosswalk'
    __table_args__ = {"schema": "attrs"}
    acs_occ = db.Column(db.String, primary_key=True)
    pums_soc = db.Column(db.String, db.ForeignKey(PumsSoc.id), primary_key=True)
    level = db.Column(db.Integer)


class IndCrosswalk(db.Model):
    __tablename__ = 'ind_crosswalk'
    __table_args__ = {"schema": "attrs"}
    acs_ind = db.Column(db.String, primary_key=True)
    pums_naics = db.Column(db.String, db.ForeignKey(PumsNaics.id), primary_key=True)
    level = db.Column(db.Integer)


class ProductCrosswalk(db.Model):
    __tablename__ = 'napcs_sctg_xwalk'
    __table_args__ = {"schema": "attrs"}
    sctg = db.Column(db.String, db.ForeignKey(Sctg.id), primary_key=True)
    napcs = db.Column(db.String, db.ForeignKey(Napcs.id), primary_key=True)


class UniversityCrosswalk(db.Model, BaseModel):
    __tablename__ = 'unitid_to_opeid6'
    __table_args__ = {"schema": "attrs"}
    opeid6 = db.Column(db.String, primary_key=True)
    university = db.Column(db.String, db.ForeignKey(University.id), primary_key=True)

    @classmethod
    def get_supported_levels(cls):
        return {
            "university": [ALL],
            "opeid": [ALL]
        }


class Opeid(BaseAttr):
    __tablename__ = 'opeid6'
    school_type = db.Column(db.Integer)
    ethnic_code = db.Column(db.Integer)


class SchoolType(BaseAttr):
    __tablename__ = 'school_type'


class ProgramLength(BaseAttr):
    __tablename__ = 'program_length'


class EthnicCode(BaseAttr):
    __tablename__ = 'ethnic_code'


class LStudy(BaseAttr):
    __tablename__ = 'lstudy'


class EnrollmentStatus(BaseAttr):
    __tablename__ = 'enrollment_status'


class IPedsRace(BaseAttr):
    __tablename__ = 'ipeds_race'


class LivingArrangement(BaseAttr):
    __tablename__ = 'living_arrangement'
    group = db.Column(db.String)


class IncomeRange(BaseAttr):
    __tablename__ = 'income_range'


class Carnegie(BaseAttr):
    __tablename__ = 'carnegie'
    depth = db.Column(db.Integer)
    parent = db.Column(db.String)
    children = db.Column(db.ARRAY(db.String))


class IPedsOcc(BaseAttr):
    __tablename__ = 'ipeds_occ'
    ipeds_occ_group = db.Column(db.String)


class IPedsExpense(BaseAttr):
    __tablename__ = 'ipeds_expense'


class AcademicRank(BaseAttr):
    __tablename__ = 'academic_rank'
    academic_group = db.Column(db.String)


class SimilarUniversities(db.Model):
    __tablename__ = 'similar_universities'
    __table_args__ = {"schema": "attrs"}
    university = db.Column(db.String, db.ForeignKey(University.id), primary_key=True)
    name = db.Column(db.String)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    carnegie = db.Column(db.String)
    carnegie_parent = db.Column(db.String)


class RateType(BaseAttr):
    __tablename__ = 'rate_type'


class CrosswalkGeoContainment(db.Model):
    __tablename__ = 'crosswalk_geo_containment'
    __table_args__ = {"schema": "attrs"}
    child_geoid = db.Column(db.String, db.ForeignKey(Geo.id), primary_key=True)
    parent_geoid = db.Column(db.String, db.ForeignKey(Geo.id),
                             primary_key=True)
    area_covered = db.Column(db.Float)
    percent_covered = db.Column(db.Float)
    parent = relationship('Geo', foreign_keys='CrosswalkGeoContainment.parent_geoid')
    child = relationship('Geo', foreign_keys='CrosswalkGeoContainment.child_geoid',
                         lazy='subquery')
