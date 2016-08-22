import json
import unittest

import datausa


class JoinAPITestCases(unittest.TestCase):

    def setUp(self):
        self.app = datausa.app.test_client()

    def test_no_crosswalk(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&geo=16000US2507000')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        target_index = headers.index('chr.yg.adult_obesity')
        acs_income_index = headers.index('acs_5yr.yg.income')
        first_row = data[0]
        assert not first_row[target_index]
        assert first_row[acs_income_index] > 0

    def test_auto_crosswalk(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&geo=16000US2507000&auto_crosswalk=1')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        target_index = headers.index('chr.yg.adult_obesity')
        chr_geo_index = headers.index('chr.yg.geo')
        first_row = data[0]
        assert first_row[target_index]
        assert first_row[chr_geo_index] == '05000US25025'

    def test_display_names(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&geo=04000US25&display_names=1')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        target_index = headers.index('chr.yg.geo_name')
        assert target_index >= 0
        first_row = data[0]
        assert first_row[target_index] == 'Massachusetts'

    def test_limit(self):
        req = self.app.get('/api/join/?required=grads_total&sumlevel=state&show=geo&limit=3')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        assert len(data) == 3

    def test_no_subs(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&geo=16000US2507000&auto_crosswalk=0')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        assert 'subs' in result
        assert not result['subs']

    def test_subs(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&geo=16000US2507000&auto_crosswalk=1')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        assert 'subs' in result
        assert 'chr.yg' in result['subs']
        assert 'geo' in result['subs']['chr.yg']
        geo_subs = result['subs']['chr.yg']['geo']
        assert len(geo_subs) == 1
        geo_sub = geo_subs[0]
        assert 'original' in geo_sub
        assert 'replacement' in geo_sub
        assert geo_sub['original'] == '16000US2507000'
        assert geo_sub['replacement'] == '05000US25025'


if __name__ == '__main__':
    unittest.main()
