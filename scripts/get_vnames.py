import pprint
from datausa.core import registrar
from datausa.database import db

data={}

for tbl in registrar.registered_models:
    data[tbl.full_name()] = [c.key for c in tbl.__table__.columns]

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(data)
