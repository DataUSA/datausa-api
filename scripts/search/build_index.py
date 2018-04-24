import os
import os.path
from whoosh import index
from whoosh.fields import Schema, ID, TEXT, NUMERIC, KEYWORD, NGRAMWORDS
from config import SEARCH_INDEX_DIR
from unidecode import unidecode


def manual_add(writer, name, display, orig_id, is_stem=False, url_name=None, zoverride=None, kind=u"geo"):
    from datausa.attrs.models import Search
    kind = unicode(kind)
    doc_obj = Search.query.filter_by(id=orig_id, kind=kind).first()
    zval = doc_obj.zvalue * 1.5 if not zoverride else zoverride
    is_stem = is_stem or doc_obj.is_stem
    if not url_name:
        url_name = doc_obj.url_name
    writer.add_document(id=doc_obj.id, name=name,
                        display=display, zvalue=zval,
                        kind=kind, sumlevel=doc_obj.sumlevel,
                        is_stem=is_stem, url_name=url_name)


def get_schema():
    return Schema(id=ID(stored=True),
                  name=NGRAMWORDS(stored=True, minsize=2, maxsize=12, at='start', queryor=True),
                  display=TEXT(stored=True),
                  zvalue=NUMERIC(stored=True),
                  kind=KEYWORD(stored=True),
                  sumlevel=KEYWORD(stored=True),
                  is_stem=NUMERIC(stored=True),
                  url_name=TEXT(stored=True))


if __name__ == '__main__':
    print "got here!"
    print SEARCH_INDEX_DIR
    if not os.path.exists(SEARCH_INDEX_DIR):
        print "got here2"
        os.mkdir(SEARCH_INDEX_DIR)
        ix = index.create_in(SEARCH_INDEX_DIR, get_schema())
        print "Creating attr index..."

    ix = index.open_dir(SEARCH_INDEX_DIR)
    writer = ix.writer()
    from datausa.attrs.models import Search
    all_objs = Search.query.all()
    for obj in all_objs:
        dname = obj.display
        stem = False if not hasattr(obj, "is_stem") else obj.is_stem
        if dname:
            dname = unicode(dname)
            dname = unidecode(dname)
            dname = unicode(dname)
            dname = dname.lower().replace(",", "")
            dname = dname.replace(".", "")
        writer.add_document(id=obj.id, name=dname,
                            display=obj.display, zvalue=obj.zvalue,
                            kind=obj.kind, sumlevel=obj.sumlevel,
                            is_stem=stem, url_name=obj.url_name)

        if obj.keywords:
            for keyword in obj.keywords:
                writer.add_document(id=obj.id, name=keyword,
                                    display=obj.display, zvalue=obj.zvalue,
                                    kind=obj.kind, sumlevel=obj.sumlevel,
                                    is_stem=stem, url_name=obj.url_name)
    # Custom synonyms to help with search
    import pandas as pd
    attrs_with_aliases = ["geo"]
    for kind in attrs_with_aliases:
        target_path = os.path.join(SEARCH_INDEX_DIR, "..", "scripts", "search", "{}_aliases.csv".format(kind))
        df = pd.read_csv(target_path)
        for geo, name, short, zval in df.values:
            for alias in short.split(","):
                alias = alias.strip()
                manual_add(writer, unicode(alias), unicode(name), unicode(geo), zoverride=zval, kind=kind)

    # --
    manual_add(writer, u'garbagemen', u'Garbagemen', '537081', kind=u'soc')
    manual_add(writer, u'doctors', u'Doctors', '291060', kind=u'soc')
    manual_add(writer, u'manhattan', u'Manhattan, NY', '05000US36061', kind=u'geo')
    manual_add(writer, u'meteorologists', u'Meteorologists', '192021', kind=u'soc')
    manual_add(writer, u'film', u'Motion Pictures & Video Industries', '5121', kind=u'naics')
    manual_add(writer, u'movies', u'Motion Pictures & Video Industries', '5121', kind=u'naics')

    writer.commit()
