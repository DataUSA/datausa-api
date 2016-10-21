from whoosh.qparser import QueryParser
from whoosh import index, sorting, scoring
from whoosh import qparser, query
from config import SEARCH_INDEX_DIR
import math
import unittest

from datausa.attrs.views import SimpleWeighter, do_search

class TestStringMethods(unittest.TestCase):
    NY_IDS = ['31000US35620', '05000US36061', '04000US36', '16000US3651000']

    def test_extra_word(self):
        headers, data, suggs, tries = do_search("new york economy")
        self.assertTrue(data[0][0] in self.NY_IDS)

    def test_manhattan(self):
        headers, data, suggs, tries = do_search("manhattan")
        self.assertEqual(data[0][0], "05000US36061")

    def test_exact_match_begin(self):
        headers, data, suggs, tries = do_search("nome")
        self.assertEqual(data[0][0], '16000US0254920')

    def test_ny(self):
        headers, data, suggs, tries = do_search("new york")
        self.assertTrue(data[0][0] in self.NY_IDS)

    def test_doc(self):
        headers, data, suggs, tries = do_search("doctor")
        self.assertEqual(data[0][0], '291060')

    def test_stl(self):
        headers, data, suggs, tries = do_search("st louis")
        self.assertEqual(data[0][0], '16000US2965000')

    def test_fortla(self):
        headers, data, suggs, tries = do_search("fort la")
        self.assertEqual(data[0][0], '16000US1224000')

    def test_bad_spelling(self):
        headers, data, suggs, tries = do_search("massachusitt")
        self.assertTrue('04000US25' in [gid[0] for gid in data[:2]])

    def test_econ(self):
        econs = ['193011', '450601']
        headers, data, suggs, tries = do_search("econ")
        self.assertTrue(data[0][0] in econs)

    def test_milford(self):
        headers, data, suggs, tries = do_search("milford nh")
        self.assertEqual(data[0][0], '16000US3347940')

    def test_bevhills(self):
        headers, data, suggs, tries = do_search("beverly hills")
        self.assertEqual(data[0][0], '16000US0606308')

    def test_kind_naics(self):
        headers, data, suggs, tries = do_search("educat", kind="naics")
        self.assertTrue(data[0][0])

    def test_ma(self):
        headers, data, suggs, tries = do_search("ma")
        self.assertEqual(data[0][0], '04000US25')

    def test_ak(self):
        headers, data, suggs, tries = do_search("ak")
        self.assertEqual(data[0][0], '04000US02')

    def test_pa(self):
        headers, data, suggs, tries = do_search("pa")
        self.assertEqual(data[0][0], '04000US42')

    def test_al(self):
        headers, data, suggs, tries = do_search("al")
        self.assertEqual(data[0][0], '04000US01')

    def test_dc(self):
        headers, data, suggs, tries = do_search("dc")
        self.assertEqual(data[0][0], '16000US1150000')

    def test_rny(self):
        headers, data, suggs, tries = do_search("rochester, ny")
        self.assertEqual(data[0][0], '16000US3663000')

    def test_cpmd(self):
        headers, data, suggs, tries = do_search("college park, md")
        self.assertEqual(data[0][0], '16000US2418750')

    def test_moco(self):
        headers, data, suggs, tries = do_search("montgomery county")
        self.assertEqual(data[0][0], '05000US24031')

    def test_pgc(self):
        headers, data, suggs, tries = do_search("prince georges county")
        self.assertEqual(data[0][0], '05000US24033')

    def test_pop_nm(self):
        _, data, _, _ = do_search("population new mexico")
        self.assertEqual(data[0][0], '04000US35')


if __name__ == '__main__':
    unittest.main()
