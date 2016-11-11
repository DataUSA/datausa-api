from whoosh.qparser import QueryParser
from whoosh import index, sorting, scoring
from whoosh import qparser, query
from config import SEARCH_INDEX_DIR
import math
import unittest
from datausa.attrs.search import do_search

ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)

facet = sorting.FieldFacet("zvalue", reverse=True)
scores = sorting.ScoreFacet()

class TestStringMethods(unittest.TestCase):
  NY_IDS = ['31000US35620', '05000US36061', '04000US36', '16000US3651000']

  def test_extra_word(self):
      data,suggs,tries,my_vars = do_search("new york economy")
      self.assertTrue(data[0][0] in self.NY_IDS)

  def test_manhattan(self):
      data,suggs,tries,my_vars = do_search("manhattan")
      self.assertEqual(data[0][0], "05000US36061")

  def test_exact_match_begin(self):
      data,suggs,tries,my_vars = do_search("nome")
      self.assertEqual(data[0][0], '16000US0254920')

  def test_ny(self):
      data,suggs,tries,my_vars = do_search("new york")
      self.assertTrue(data[0][0] in self.NY_IDS)

  def test_doc(self):
      data,suggs,tries,my_vars = do_search("doctor")
      self.assertEqual(data[0][0], '291060')

  def test_stl(self):
      data,suggs,tries,my_vars = do_search("st louis")
      self.assertEqual(data[0][0], '16000US2965000')

  def test_fortla(self):
        data,suggs,tries,my_vars = do_search("fort lau")
        self.assertEqual(data[0][0], '16000US1224000')

  def test_bad_spelling(self):
        data,suggs,tries,my_vars = do_search("massachusitt")
        self.assertEqual(data[0][0], '04000US25')

  def test_econ(self):
        econs = ['193011', '450601', '01000US', '193011']
        data,suggs,tries,my_vars = do_search("econ")
        self.assertTrue(data[0][0] in econs)

  def test_milford(self):
        data,suggs,tries,my_vars = do_search("milford nh")
        self.assertEqual(data[0][0], '16000US3347940')

  def test_bevhills(self):
        data,suggs,tries,my_vars = do_search("beverly hills")
        self.assertEqual(data[0][0], '16000US0606308')

  def test_kind_naics(self):
        data,suggs,tries,my_vars = do_search("educat", kind="naics")
        self.assertTrue(data[0][0])

  def test_ma(self):
        data,suggs,tries,my_vars = do_search("ma")
        self.assertEqual(data[0][0], '04000US25')

  def test_ak(self):
        data,suggs,tries,my_vars = do_search("ak")
        self.assertEqual(data[0][0], '04000US02')

  def test_pa(self):
        data,suggs,tries,my_vars = do_search("pa")
        self.assertEqual(data[0][0], '04000US42')

  def test_al(self):
        data,suggs,tries,my_vars = do_search("al")
        self.assertEqual(data[0][0], '04000US01')

  def test_dc(self):
        data,suggs,tries,my_vars = do_search("dc")
        self.assertEqual(data[0][0], '16000US1150000')

  def test_rny(self):
        data,suggs,tries,my_vars = do_search("rochester, ny")
        self.assertEqual(data[0][0], '16000US3663000')

  def test_cpmd(self):
        data,suggs,tries,my_vars = do_search("college park, md")
        self.assertEqual(data[0][0], '16000US2418750')

  def test_moco(self):
        data,suggs,tries,my_vars = do_search("montgomery county")
        self.assertEqual(data[0][0], '05000US24031')

  def test_pgc(self):
        data,suggs,tries,my_vars = do_search("prince georges county")
        self.assertEqual(data[0][0], '05000US24033')

  def test_travel_time(self):
        data,suggs,tries,my_vars = do_search("travel time")
        self.assertEqual(data[0][0], '01000US')

  def test_commute_time(self):
        data,suggs,tries,my_vars = do_search("commute time")
        self.assertEqual(data[0][0], '01000US')

  def test_boston_travel_time(self):
        data,suggs,tries,my_vars = do_search("boston travel time")
        self.assertEqual(data[0][0], '16000US2507000')

  def test_nj_travel_time(self):
        data,suggs,tries,my_vars = do_search("economy in new jersey")
        ids = [row[0] for row in data[:3]]
        self.assertTrue('04000US34' in ids)
        self.assertEqual(ids[0], '16000US1820152')

  def test_obesity(self):
        data,suggs,tries,my_vars = do_search("obesity")
        self.assertEqual(data[0][0], '01000US')

  def test_vietnamese_wyoming(self):
        data,suggs,tries,my_vars = do_search("vietnamese speakers in wyoming")
        ids = [row[0] for row in data]
        self.assertTrue('04000US56' in ids[:2])

  def test_polish_chicago(self):
        data,suggs,tries,my_vars = do_search("polish speakers in chicago")
        self.assertEqual(data[0][0], '16000US1714000')

  def test_native_cambr(self):
        data,suggs,tries,my_vars = do_search("native born in cambridge")
        self.assertEqual(data[0][0], '16000US2511000')

  def test_fr_cambr(self):
        data,suggs,tries,my_vars = do_search("french in cambridge")
        self.assertEqual(data[0][0], '16000US2511000')

  def test_chil_nm(self):
        data,suggs,tries,my_vars = do_search("chileans in new mexico")
        self.assertEqual(data[0][0], '04000US35')

  def test_swiss_nj(self):
        data,suggs,tries,my_vars = do_search("swiss in new jersey")
        self.assertEqual(data[0][0], '04000US34')

  def test_cuba_montana(self):
        data,suggs,tries,my_vars = do_search("cubans in montana")
        self.assertEqual(data[0][0], '04000US30')

  def test_il_fl(self):
        data,suggs,tries,my_vars = do_search("israelis in florida")
        self.assertEqual(data[0][0], '04000US12')


  def test_citizenship(self):
        data,suggs,tries,my_vars = do_search("citizenship")
        self.assertEqual(data[0][0], '01000US')

  def test_citizenship(self):
        data,suggs,tries,my_vars = do_search("citizenship in florida")
        self.assertEqual(data[0][0], '04000US12')

  def test_ga(self):
        data,suggs,tries,my_vars = do_search("georgia")
        self.assertEqual(data[0][0], '04000US13')


if __name__ == '__main__':
    unittest.main()
