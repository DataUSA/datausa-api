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
    def col_strs(cls):
        return [str(col) for col in cls.__table__.columns]

class ApiObject(object):
    def __init__(self, **kwargs):
        allowed = ["vars_needed", "vars_and_vals", "values",
                   "shows_and_levels", "force", "where", "order",
                   "sort", "limit", "exclude"]
        self._year = None
        for keyword, value in kwargs.items():
            if keyword in allowed:
                setattr(self, keyword, value)
            else:
                raise DataUSAException("Invalid ApiObject attribute")
        if self.limit:
            self.limit = int(self.limit)
        self.subs = {}
        self.table_list = []
        if self.exclude:
            self.exclude = self.exclude.split(",")
        if hasattr(self, "year") and self.year != ALL:
            self._year = self.year
        self.force_schema = None
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
