from sqlalchemy.orm.attributes import InstrumentedAttribute

def get_columns(tbl):
    return tbl.__table__.columns

# possible_variables = [col.key for t in registered_models for col in t.__table__.columns]
# def attribute_names(cls):
#     return [prop.key for prop in class_mapper(cls).iterate_properties
#         if isinstance(prop, ColumnProperty)]

# def get_columns(tbl):
#     cols = []
#     for item,val in tbl.__dict__.items():
#         if isinstance(val, InstrumentedAttribute) and not item.startswith("_"):
#             cols.append(val)
#     # print tbl.__table__.columns
#     return cols
