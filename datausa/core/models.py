from datausa.core.exceptions import DataUSAException
from datausa.attrs.consts import ALL, OR


class BaseModel(object):
    median_moe = None
    size = None
    source_title = ''
    source_link = ''
    source_org = ''
    # def __init__(levels, moe, size):
    #     self.supported_levels = levels
    #     self.median_moe = moe
    #     self.size = size

    @classmethod
    def get_supported_level(cls):
        return {}

    @classmethod
    def info(cls, api_obj=None):
        dataset = cls.source_title
        if api_obj and api_obj.get_year():
            dataset = "{} {}".format(api_obj.get_year(), dataset)
        return {
            "dataset": dataset,
            "org": cls.source_org,
            "table": cls.__tablename__,
            "link": cls.source_link,
            "supported_levels": cls.get_supported_levels(),
        }

    @classmethod
    def full_name(cls):
        table_name = cls.__tablename__
        schema_name = cls.__table_args__["schema"]
        return "{}.{}".format(schema_name, table_name)

    @classmethod
    def get_schema_name(cls):
        return cls.__table_args__["schema"]

    @classmethod
    def col_strs(cls, short_name=False):
        results = [str(col) for col in cls.__table__.columns]
        if short_name:
            results = [col_name.split(".")[-1] for col_name in results]
        return results

    @classmethod
    def can_show(cls, attr, lvl):
        supported = cls.get_supported_levels()
        return attr in supported and lvl in supported[attr]

class ApiObject(object):
    def __init__(self, **kwargs):
        allowed = ["vars_needed", "vars_and_vals", "values",
                   "shows_and_levels", "force", "where", "order",
                   "sort", "limit", "exclude", "auto_crosswalk",
                   "display_names", "offset"]
        self._year = None
        self.auto_crosswalk = False
        self.display_names = False
        self.offset = None
        for keyword, value in kwargs.items():
            if keyword in allowed:
                setattr(self, keyword, value)
            else:
                raise DataUSAException("Invalid ApiObject attribute")
        if self.limit:
            self.limit = int(self.limit)
        if self.offset:
            self.offset = int(self.offset)
        self.subs = {}
        self.table_list = []
        self.warnings = []
        if self.exclude:
            self.exclude = self.exclude.split(",")
        if hasattr(self, "year") and self.year != ALL:
            self._year = self.year
        self.force_schema = None
        self.auto_crosswalk = self.auto_crosswalk in [True, 'true', '1']
        self.display_names = self.display_names in ['true', '1']
        # if not "geo" in self.shows_and_levels and "geo" in self.vars_and_vals:
        #     if self.vars_and_vals["geo"]:
        #         prefix = self.vars_and_vals["geo"][:3]
        #         lookup = {"010": "nation", "040": "state", "050": "county", "310":"msa", "795":"puma", "160":"place"}
        #         if prefix in lookup:
        #             self.shows_and_levels["geo"] = lookup[prefix]
    def set_year(self, yr):
        self._year = str(int(yr))

    def get_year(self):
        return self._year

    def capture_logic(self, table_list):
        self.table_list = table_list

    def warn(self, msg):
        self.warnings.append(msg)

    def record_sub(self, tbl, col, orig_val, new_val):
        deltas = [{"original": ov, "replacement": nv} for ov, nv in zip(orig_val, new_val) if ov != nv]

        tbl_name = tbl.full_name()
        if tbl_name not in self.subs:
            self.subs[tbl_name] = {}
        if col not in self.subs[tbl_name]:
            self.subs[tbl_name][col] = {}
        self.subs[tbl_name][col] = deltas

    def where_vars(self):
        if not hasattr(self, "where") or not self.where:
            return []
        # split by commas
        wheres = self.where.split(",")
        # then split by colons, and take the last item after period e.g.
        var_names = [x.split(":")[0].split(".")[-1] for x in wheres]
        var_names = [x for x in var_names if x != 'sumlevel']
        # so where=year:2014,grads_total.degree:5 => ['year', 'degree']
        return var_names
