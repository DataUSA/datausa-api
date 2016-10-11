import json
import unittest
from fuzzywuzzy import process

from datausa.attrs.views import do_search
from datausa.core.views import manager
from datausa.attrs.var_search import var_search

class TestVarSearch(unittest.TestCase):

    def test_spanish_ny(self):
        q = 'spanish speakers in new mexico'
        results = var_search(q)
        assert "vars" in results
        assert len(results["vars"]) == 1
        first_var = results["vars"][0]
        assert first_var["required"] == "num_speakers"
        assert first_var["language"] == "003" # spanish

    def test_stat_search_pop(self):
        q = 'population of west virginia'
        results = var_search(q)
        assert 'vars' in results
        assert len(results["vars"]) == 1
        first_var = results["vars"][0]
        assert first_var["required"] == "pop"

    def test_stat_search_obesity(self):
        q = 'obesity in chi'
        results = var_search(q)
        assert len(results["vars"]) >= 1
        first_var = results["vars"][0]
        assert first_var["required"] == "adult_obesity"

if __name__ == '__main__':
    unittest.main()
