import json
import unittest

import datausa


class JoinAPITestCases(unittest.TestCase):

    def setUp(self):
        self.app = datausa.app.test_client()

    def get_data(self, url):
        req = self.app.get(url)
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        return data, headers

    def test_geo_crosswalk(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&where=income.geo:16000US2507000,adult_obesity.sumlevel:county&year=latest')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        target_index = headers.index('chr.yg.adult_obesity')
        chr_geo_index = headers.index('chr.yg.geo')
        first_row = data[0]
        assert len(data) == 1
        assert first_row[target_index]
        assert first_row[chr_geo_index] == '05000US25025'

    def test_join_but_no_geo_crosswalk(self):
        req = self.app.get('/api/join/?required=pop_black,pop_white,income&sumlevel=all&show=geo&where=income.geo:16000US2511000&year=latest')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        target_index = headers.index('acs_5yr.yg_race.pop_black')
        yg_race_geo_index = headers.index('acs_5yr.yg_race.geo')
        first_row = data[0]
        assert len(data) == 1
        assert first_row[target_index]
        assert first_row[yg_race_geo_index] == '16000US2511000'

    def test_display_names(self):
        req = self.app.get('/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&where=adult_obesity.geo:04000US25&display_names=1')
        result = json.loads(req.data)
        assert 'data' in result
        data = result['data']
        headers = result['headers']
        target_index = headers.index('chr.yg.geo_name')
        assert target_index >= 0
        first_row = data[0]
        assert first_row[target_index] == 'Massachusetts'

    def test_limit(self):
        url = '/api/join/?required=grads_total&sumlevel=all&show=geo&limit=3'
        data, _ = self.get_data(url)
        assert len(data) == 3

    def test_geos_crosswalk_3vars(self):
        url = '/api/join/?required=adult_obesity,avg_wage,income&sumlevel=all&show=geo&where=income.geo:16000US2507000,adult_obesity.sumlevel:county,grads_total.sumlevel:county&year=latest'
        data, _ = self.get_data(url)
        assert len(data) >= 1

    def test_cip_crosswalk(self):
        url = '/api/join/?required=avg_wage,value&sumlevel=all&show=cip&where=value.cip:010000'
        data, _ = self.get_data(url)
        assert len(data) >= 1

    def test_geos_2vars_latest(self):
        url = '/api/join/?required=adult_obesity,income&sumlevel=all&show=geo&where=income.geo:04000US25,adult_obesity.geo:04000US25&year=latest'
        data, _ = self.get_data(url)
        assert len(data) == 1

    def test_ipeds_acs_geo_join(self):
        url = '/api/join/?required=grads_total,income&sumlevel=all&show=geo&where=income.geo:16000US2507000,grads_total.sumlevel:state&year=latest'
        data, _ = self.get_data(url)
        assert len(data) == 1

    def test_puma_to_state(self):
        url = '/api/join/?required=avg_wage,grads_total,income&show=geo&where=avg_wage.sumlevel:puma,grads_total.geo:04000US25,avg_wage.geo:79500US2500100,income.sumlevel:state&year=latest'
        data, _ = self.get_data(url)
        assert len(data) == 1

    def test_puma_to_state_and_county(self):
        url = '/api/join/?required=avg_wage,grads_total,income&show=geo&where=avg_wage.geo:79500US2500506,grads_total.sumlevel:state,income.sumlevel:county&year=latest'
        data, _ = self.get_data(url)
        assert len(data) == 1

    def test_bug(self):
        url = '/api/join/?required=grads_total,adult_obesity&sumlevel=all&show=geo&where=grads_total.geo:16000US2511000,adult_obesity.sumlevel:state&year=latest'
        data, _ = self.get_data(url)
        assert len(data) == 1

    def test_bug2(self):
        url = '/api/join/?required=avg_wage,income&show=geo&where=avg_wage.geo:79500US2500506,income.sumlevel:state&year=latest'
        data, _ = self.get_data(url)
        assert len(data) == 1

    def test_national_containment(self):
        url='/api/join/?required=grads_total,adult_obesity&sumlevel=all&show=geo&limit=5&where=grads_total.geo:01000US,adult_obesity.sumlevel:county'
        data, _ = self.get_data(url)
        assert len(data) >= 1

    def test_geo_non_crosswalk(self):
        url='/api/join/?required=grads_total,adult_obesity&show=geo&limit=1&where=grads_total.geo:16000US2511000&auto_crosswalk=0'
        data, headers = self.get_data(url)
        target_index = headers.index('chr.yg.geo')
        first_row = data[0]
        assert first_row[target_index] is None

    def test_cip_crosswalk(self):
        url='/api/join/?required=avg_wage,grads_total&show=cip&limit=1&where=grads_total.cip:090401&auto_crosswalk=1'
        data, headers = self.get_data(url)
        target_index = headers.index('pums_1yr.yc.cip')
        first_row = data[0]
        assert first_row[target_index] == '09'

    def test_cip_no_crosswalk(self):
        url='/api/join/?required=avg_wage,grads_total&show=cip&limit=1&where=grads_total.cip:090401&auto_crosswalk=0'
        data, headers = self.get_data(url)
        target_index = headers.index('pums_1yr.yc.cip')
        first_row = data[0]
        assert first_row[target_index] is None

if __name__ == '__main__':
    unittest.main()
