from whoosh.qparser import QueryParser
from whoosh import index, sorting, scoring
from whoosh import qparser
from config import SEARCH_INDEX_DIR
import math

class CWeighting(scoring.Weighting):
    def __init__(self, fullterm):
        self.termweight = scoring.BM25F()
        self.fullterm = fullterm.lower().strip()
    def score(self, searcher, fieldnum, text, docnum, weight, qf=1):
        # Get the BM25 score for this term in this document
        bm25 = self.termweight.scorer(searcher, fieldnum, text, docnum)
        q=qp.parse(text)
        score_me = bm25.score(q.matcher(searcher))
        name = searcher.stored_fields(docnum).get("name")
        zvalue = searcher.stored_fields(docnum).get("zvalue")
        if name == self.fullterm:
            return score_me * 10
        elif name.startswith(self.fullterm):
            if zvalue > 1:
                return (score_me * 5.75) + (15 * zvalue)
            else:
                return score_me * 5.75 + -15 * zvalue
        elif text.startswith(name):
            return (score_me * 1.75) + (10 * zvalue)
        return (score_me * 0.75) + (zvalue * 0.25)

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


data,suggs,tries = do_search("nome")
assert data[0][0] == '16000US0254920'
data,suggs,tries = do_search("new york")
nys = ['31000US35620', '05000US36061', '04000US36', '16000US3651000']
assert data[0][0] in nys 

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
