from datausa.core.exceptions import DataUSAException

class BaseModel(object):
    median_moe = None
    size = None

    # def __init__(levels, moe, size):
    #     self.supported_levels = levels
    #     self.median_moe = moe
    #     self.size = size

    @classmethod
    def get_supported_level(cls):
        return {}

    @classmethod
    def info(cls):
        dataset = cls.__table_args__["schema"]
        return {
            "dataset": dataset,
            "table": cls.__tablename__,
            "supported_levels": cls.get_supported_levels(),
        }

class ApiObject(object):
    def __init__(self, **kwargs):
        allowed = ["vars_needed", "vars_and_vals", "values", "shows_and_levels",
                   "force", "where", "order", "sort", "limit"]
        for keyword, value in kwargs.items():
            if keyword in allowed:
                setattr(self, keyword, value)
            else:
                raise DataUSAException("Invalid ApiObject attribute")
        if self.limit:
            self.limit = int(self.limit)
        self.subs = {}