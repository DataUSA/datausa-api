from whoosh.qparser import QueryParser
from whoosh import index, sorting, scoring
from whoosh import qparser
from config import SEARCH_INDEX_DIR
import math

from test_search import CWeighting
ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)

facet = sorting.FieldFacet("zvalue", reverse=True)
scores = sorting.ScoreFacet()


def do_search(txt, sumlevel=None, kind=None, tries=0):
    if kind:
        txt += " AND kind:{}".format(kind)
    if sumlevel:
        txt += " AND sumlevel:{}".format(sumlevel)
    if tries > 2:
        return [],[]
    q = qp.parse(txt)

    with ix.searcher(weighting=CWeighting(txt)) as s:
        corrector = s.corrector("display")
        suggs = corrector.suggest(txt, limit=10, maxdist=2, prefix=3)
        results = s.search(q, sortedby=[scores])
        data = [[r["id"], r["name"], r["zvalue"],
                 r["kind"], r["display"], r["sumlevel"]]
                for r in results]
        if not data and suggs:
            return do_search(suggs[0], sumlevel, kind, tries=tries+1)
        return data, suggs, tries




if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        txt = sys.argv[1]# "nome"
        res =  do_search(txt)
        print res
        if not res:
            print "did you mean?"
            with ix.searcher() as s:
                corrector = s.corrector("display")
                print corrector.suggest(txt, limit=3, maxdist=2)
