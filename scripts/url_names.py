
from datausa.attrs.models import Geo
from datausa.database import db

def hyphenate(x):
    ctr = {ord(c):u'-' for c in [',', ' ', '-']}
    tmp = unicode(x).translate(ctr)
    return tmp.replace('--', '-')

sumlevels = ['160']

count = 1
for sumlevel in sumlevels:
    filters = [Geo.id.startswith(sumlevel)]
    objs = Geo.query.filter(*filters).all()
    for o in objs:
        o.url_name = hyphenate(o.display_name)
        print o.url_name
        db.session.add(o)

        if count > 10000:
            db.session.commit()
            count = 1

db.session.commit()


