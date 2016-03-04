from whoosh.qparser import QueryParser
from whoosh import index, sorting, scoring
from whoosh import qparser, query
from config import SEARCH_INDEX_DIR
import math
import unittest


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
            return score_me * 30 + (25 * abs(zvalue))
        elif name.startswith(self.fullterm):
            if zvalue > 0:
                return (score_me * 5.75) + (25 * zvalue)
            else:
                return score_me * 5.75 + (1 - abs(zvalue) * 25)
        elif text.startswith(name):
            return (score_me * 1.75) + (10 * zvalue)
        return (score_me * 0.75) + (zvalue * 0.25)

ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)

facet = sorting.FieldFacet("zvalue", reverse=True)
scores = sorting.ScoreFacet()


def do_search(txt, sumlevel=None, kind=None, tries=0, limit=10):
    txt = txt.replace(",", "")

    my_filter = None
    if kind and sumlevel:
        kf = query.Term("kind", kind)
        sf = query.Term("sumlevel", sumlevel)
        my_filter = query.And([kf, sf])
    elif kind:
        my_filter = query.Term("kind", kind)
    elif sumlevel:
        my_filter = query.Term("sumlevel", sumlevel)
    if tries > 2:
        return [],[]
    q = qp.parse(txt)

    with ix.searcher(weighting=CWeighting(txt)) as s:
        if len(txt) > 2:
            corrector = s.corrector("display")
            suggs = corrector.suggest(txt, limit=10, maxdist=2, prefix=3)
        else:
            suggs = []
        results = s.search_page(q, 1, sortedby=[scores], pagelen=20, filter=my_filter)
        data = [[r["id"], r["name"], r["zvalue"],
                 r["kind"], r["display"], r["sumlevel"] if "sumlevel" in r else ""]
                for r in results]
        if not data and suggs:
            return do_search(suggs[0], sumlevel, kind, tries=tries+1, limit=limit)
        return data, suggs, tries



class TestStringMethods(unittest.TestCase):
  NY_IDS = ['31000US35620', '05000US36061', '04000US36', '16000US3651000']

  def test_extra_word(self):
      data,suggs,tries = do_search("new york economy")
      self.assertTrue(data[0][0] in self.NY_IDS)

  def test_manhattan(self):
      data,suggs,tries = do_search("manhattan")
      self.assertEqual(data[0][0], "05000US36061")

  def test_exact_match_begin(self):
      data,suggs,tries = do_search("nome")
      self.assertEqual(data[0][0], '16000US0254920')

  def test_ny(self):
      data,suggs,tries = do_search("new york")
      self.assertTrue(data[0][0] in self.NY_IDS)

  def test_doc(self):
      data,suggs,tries = do_search("doctor")
      self.assertEqual(data[0][0], '291060')

  def test_stl(self):
      data,suggs,tries = do_search("st louis")
      self.assertEqual(data[0][0], '16000US2965000')

  def test_wmass(self):
        data,suggs,tries = do_search("western massachusetts")
        self.assertEqual(data[0][0], '04000US25')

  def test_bad_spelling(self):
        data,suggs,tries = do_search("massachusitt")
        self.assertEqual(data[0][0], '04000US25')

  def test_econ(self):
        econs = ['193011', '450601']
        data,suggs,tries = do_search("econ")
        self.assertTrue(data[0][0] in econs)

  def test_milford(self):
        data,suggs,tries = do_search("milford nh")
        self.assertEqual(data[0][0], '16000US3347940')

  def test_bevhills(self):
        data,suggs,tries = do_search("beverly hills")
        self.assertEqual(data[0][0], '16000US0606308')

  def test_kind_naics(self):
        data,suggs,tries = do_search("educat", kind="naics")
        self.assertTrue(data[0][0])

  def test_ma(self):
        data,suggs,tries = do_search("ma")
        self.assertEqual(data[0][0], '04000US25')

  def test_ak(self):
        data,suggs,tries = do_search("ak")
        self.assertEqual(data[0][0], '04000US02')

  def test_pa(self):
        data,suggs,tries = do_search("pa")
        self.assertEqual(data[0][0], '04000US42')

  def test_al(self):
        data,suggs,tries = do_search("al")
        self.assertEqual(data[0][0], '04000US01')

  def test_dc(self):
        data,suggs,tries = do_search("dc")
        self.assertEqual(data[0][0], '16000US1150000')

  def test_rny(self):
        data,suggs,tries = do_search("rochester, ny")
        self.assertEqual(data[0][0], '16000US3663000')

  def test_cpmd(self):
        data,suggs,tries = do_search("college park, md")
        self.assertEqual(data[0][0], '16000US2418750')

if __name__ == '__main__':
    unittest.main()
