import os
import os.path
from whoosh import index
from whoosh.fields import Schema, ID, TEXT, NUMERIC, KEYWORD, NGRAM
from config import SEARCH_INDEX_DIR

def get_schema():
    return Schema(id=ID(unique=True, stored=True),
                  name=NGRAM(phrase=True, stored=True, minsize=2),
                  display=TEXT(stored=True),
                  zvalue=NUMERIC(stored=True),
                  kind=KEYWORD(stored=True),
                  sumlevel=KEYWORD(stored=True))

if __name__ == '__main__':
    if not os.path.exists(SEARCH_INDEX_DIR):
        os.mkdir(SEARCH_INDEX_DIR)
        ix = index.create_in(SEARCH_INDEX_DIR, get_schema())
        print "Creating attr index..."

    ix = index.open_dir(SEARCH_INDEX_DIR)
    writer = ix.writer()
    from datausa.attrs.models import Search
    all_objs = Search.query.all()
    for obj in all_objs:
        dname = obj.display
        if dname:
            dname = dname.lower().replace(",", "")
            dname = dname.replace(".", "")
        writer.add_document(id=obj.id, name=dname,
                            display=obj.display, zvalue=obj.zvalue,
                            kind=obj.kind, sumlevel=obj.sumlevel)

    # Custom synonyms to help with search
    doc_obj = Search.query.filter_by(id="291060").first()
    writer.add_document(id=doc_obj.id, name=u'doctors',
                        display=u'Doctors', zvalue=doc_obj.zvalue*1.5,
                        kind=doc_obj.kind, sumlevel=doc_obj.sumlevel)
    writer.commit()
