import os
import os.path
from whoosh import index
from whoosh.fields import Schema, ID, TEXT, NUMERIC, KEYWORD, NGRAM, NGRAMWORDS
from whoosh.fields import BOOLEAN
from config import SEARCH_INDEX_DIR
from datausa.database import db

from datausa.attrs.models import Geo
from datausa.acs.automap_models import Acs5_Yg
geos = Geo.query.filter(Geo.id.like('160%')).all()

url_map = {}

for g in geos:
    if g.url_name and g.url_name not in url_map:
        url_map[g.url_name] = []
    if g.url_name:
        url_map[g.url_name].append(g)

# now we have a list of all g's
url_map = {k:v for k,v in url_map.items() if v and len(v) > 1}

# get first ...
for url_name, glist in url_map.items():
    if url_name.endswith("-pr") or url_name == 'chevy-chase-md':
        print "skipping pr for now..."
        continue
    print "working on", url_name
    if len(glist) == 2:
        data = []
        has_ran = False
        for g in glist:
            moi = Acs5_Yg.query.filter(Acs5_Yg.year == 2014, Acs5_Yg.geo == g.id).first()
            parents, headers = Geo.parents(g.id)
            county = None
            for p in parents:
                print p, "TEST"
                if p[0][:3] == '050':
                    county = p[2].split("-county-")[0].lower()
            if not moi:
                continue
            pop = moi.pop
            data.append([g.url_name, g.id, pop, county, g])
            has_ran = True
        if not has_ran:
            print "skipping", url_name
            continue
        # select the place with less pop
        from operator import attrgetter
        min_pl = min(data, key=lambda x: x[2])
        print data
        print min_pl
        print "RENAMING!!!!"
        geo_obj = min_pl[-1]
        print geo_obj.name, "|", geo_obj.display_name , "|", geo_obj.url_name
        newc = u", {} County".format(min_pl[-2].title())
        new_name = geo_obj.name.strip() + newc
        new_disp = geo_obj.display_name.replace(geo_obj.name, new_name)
        print "min_pl-2=",min_pl[-2]
        new_url = geo_obj.url_name[:-3] + u'-{}-county'.format(min_pl[-2]) + geo_obj.url_name[-3:]
        print "========="
        print "GEOid", geo_obj.id
        print "original", geo_obj.name
        print "original", geo_obj.display_name
        print "original", geo_obj.url_name
        print "The new name", new_name
        print "The new disp", new_disp
        print "The new url", new_url
        geo_obj.name = new_name
        geo_obj.display_name = new_disp
        geo_obj.url_name = new_url
        user_ok = raw_input("DO I HAVE THE OK? ")
        if user_ok == "AOK":
            db.session.add(geo_obj)
            db.session.commit()
    else:
        print "url_name has more than 2!!!!!!", url_name
