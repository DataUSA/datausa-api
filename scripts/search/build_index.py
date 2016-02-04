import os
import os.path
from whoosh import index
from whoosh.fields import Schema, ID, TEXT, NUMERIC, KEYWORD, NGRAM, NGRAMWORDS
from whoosh.fields import BOOLEAN
from config import SEARCH_INDEX_DIR


def manual_add(writer, name, display, orig_id, is_stem=False, url_name=None):
    from datausa.attrs.models import Search
    doc_obj = Search.query.filter_by(id=orig_id).first()
    writer.add_document(id=doc_obj.id, name=name,
                        display=display, zvalue=doc_obj.zvalue*1.5,
                        kind=doc_obj.kind, sumlevel=doc_obj.sumlevel,
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
            dname = dname.lower().replace(",", "")
            dname = dname.replace(".", "")
        writer.add_document(id=obj.id, name=dname,
                            display=obj.display, zvalue=obj.zvalue,
                            kind=obj.kind, sumlevel=obj.sumlevel,
                            is_stem=stem, url_name=obj.url_name)

    # Custom synonyms to help with search
    manual_add(writer, u'nyc', u'New York', '16000US3651000', url_name=u'new-york-ny')
    manual_add(writer, u'la', u'Los Angeles', '16000US0644000', url_name=u'los-angeles-ca')
    manual_add(writer, u'garbagemen', u'Garbagemen', '537081')
    manual_add(writer, u'doctors', u'Doctors', '291060')
    manual_add(writer, u'manhattan', u'Manhattan, NY', '05000US36061')
    manual_add(writer, u'meteorologists', u'Meteorologists', '192021')
    writer.commit()
