import json
import unittest
from fuzzywuzzy import process

from datausa.attrs.views import do_search
from datausa.core.views import manager
from datausa.attrs.var_search import var_search

class TestVarSearch(unittest.TestCase):

  def test_stat_search_obesity(self):
      q = 'obesity in new york'
      results = var_search(q)
      assert "adult_obesity" in results


  def test_stat_search_pop(self):
      q = 'population of west virginia'
      results = var_search(q)
      assert "pop" in results

if __name__ == '__main__':
    unittest.main()
