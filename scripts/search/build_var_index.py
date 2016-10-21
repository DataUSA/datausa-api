import os
import os.path

from whoosh import index
from whoosh.fields import Schema, TEXT, NGRAMWORDS
from config import VAR_INDEX_DIR

def get_schema():
    return Schema(related_vars=TEXT(stored=True),
                  name=NGRAMWORDS(stored=True, minsize=2, maxsize=12, at='start', queryor=True),
                  description=TEXT(stored=True),
                  section=TEXT(stored=True),
                  related_attrs=TEXT(stored=True))

if __name__ == '__main__':
    print("Building index...")
    if not os.path.exists(VAR_INDEX_DIR):
        os.mkdir(VAR_INDEX_DIR)
        ix = index.create_in(VAR_INDEX_DIR, get_schema())
        print("Creating variables index...")

    ix = index.open_dir(VAR_INDEX_DIR)
    writer = ix.writer()

    all_vars = [
        [u'adult_obesity,diabetes', u'obesity', u'Obesity prevalence', u'health', u'geo'],
        [u'adult_obesity,diabetes', u'diabetes', u'Diabetes prevalence', u'health', u'geo'],
        [u'pop,age', u'population', u'Population', u'demographics', u'geo'],
    ]

    for related_vars, name, description, section, related_attrs in all_vars:
        writer.add_document(related_vars=related_vars, name=name,
                            description=description, section=section,
                            related_attrs=related_attrs)
    writer.commit()
