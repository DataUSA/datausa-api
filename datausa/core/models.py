from datausa.core.exceptions import DataUSAException

class BaseModel(object):
    supported_levels = {}
    median_moe = None
    size = None

    # def __init__(levels, moe, size):
    #     self.supported_levels = levels
    #     self.median_moe = moe
    #     self.size = size

    @classmethod
    def info(cls):
        dataset = cls.__table_args__["schema"]
        return {
            "dataset": dataset,
            "table": cls.__tablename__,
            "api_endpoint": "/api/" + dataset,
            "supported_levels": cls.supported_levels,
            # "size": cls.size,
            # "median_moe": cls.median_moe
        }


class ApiObject(object):
    def __init__(self, **kwargs):
        allowed = ["vars_needed", "vars_and_vals", "values", "shows_and_levels", "where"]
        for keyword, value in kwargs.items():
            if keyword in allowed:
                setattr(self, keyword, value)
            else:
                raise DataUSAException("Invalid ApiObject attribute")
