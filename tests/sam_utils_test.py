from datetime import datetime as dt
import os
import shutil
import sys
import unittest
from unittest.mock import patch

import responses
import requests_mock

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from tests.test_utils import get_zip_in_memory, get_day_side_effect
from tests import mock_opps
from utils.sam_utils import get_org_info, write_zip_content, get_notice_data, get_notice_type,\
                            schematize_opp, naics_filter, get_dates_from_opp, find_yesterdays_opps

from utils.request_utils import  get_opp_request_details, get_opps


class SamUtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.zip_in_memory = get_zip_in_memory()
        self.opp = mock_opps.mock_opp_one
        self.maxDiff = None
        
    def tearDown(self):
        self.zip_in_memory = None
        self.opp = None

    @patch('utils.sam_utils.get_org_request_details')    
    @requests_mock.Mocker()
    def test_get_org_info(self, mock_get_org_request_details, mock_request):
        fhorgid = '123'
        url = f'https://api.sam.gov/prod/federalorganizations/v1/orgs?fhorgid={fhorgid}'
        mock_get_org_request_details.return_value = (url, {})
        response = {'orglist': [{'fhagencyorgname': 'agency', 'fhorgname': 'org'}]}
        mock_request.register_uri('GET',
                                  url = url,
                                  json = response,
                                  status_code = 200)
        result = get_org_info(fhorgid)
        expected = ('agency', 'org')
        self.assertEqual(result, expected)

    def test_write_zip_content(self):    
        content = self.zip_in_memory
        try:
            result = write_zip_content(content, 'temp_archive')
            expected = ['temp_archive/test.pdf']
            self.assertEqual(result, expected)
        finally:
            file_to_delete = os.path.join(os.getcwd(), 'attachments', 'test.pdf')
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
            if os.path.exists('temp_archive'):
                shutil.rmtree('temp_archive')

    def test_get_notice_data(self):
        opp_data = {'pointOfContacts': [{'email': 'test@test.gov'}],
                    'psc':[{'code':'test'}],
                    'naics': [{"code": ["test"]}],
                    'title': 'test',
                    'typeOfSetAside':'test'}

        opp_id = '123'
        result = get_notice_data(opp_data, opp_id)
        expected = {'classcod': 'test',
                    'naics': 'test',
                    'subject': 'Test', #title-cased by function
                    'url': f'https://beta.sam.gov/opp/{opp_id}/view',
                    'setaside': 'test',
                    'emails': ['test@test.gov']}
        self.assertEqual(result, expected)

    def test_get_notice_type_presol(self):
        expected = get_notice_type('p')
        result = 'Presolicitation'
        self.assertEqual(result, expected)
    
    def test_get_notice_type_combine(self):
        expected = get_notice_type('k')
        result = 'Combined Synopsis/Solicitation'
        self.assertEqual(result, expected)

    def test_get_notice_type_sol(self):
        expected = get_notice_type('o')
        result = 'Solicitation'
        self.assertEqual(result, expected)

    def test_get_notice_type_no_match(self):
        expected = get_notice_type('u')
        result = None
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_notice_data')
    @patch('utils.sam_utils.get_org_info')
    @patch('utils.sam_utils.get_notice_type')
    def test_schematize_opp(self, m_get_notice_type, m_get_org_info, m_get_notice_data):
        m_get_notice_type.return_value = 'test'
        m_get_org_info.return_value = ('agency', 'office')
        notice_data = {'classcod': 'test',
                       'naics': 'test',
                       'subject': 'test',
                       'url': 'https://beta.sam.gov/opp/123/view',
                       'setaside': 'test',
                       'emails': ['test@test.gov']}
        required_data = {'notice type':'Award Notice',
                         'solnbr': 'FY1912306',
                         'agency': 'DEPARTMENT OF DEFENSE',
                         'compliant': 0,
                         'office': 'DEPT OF THE NAVY',
                         'opp_id': '532e8551391a4ba784e1e186656b6a39',
                         'attachments':[]}
        m_get_notice_data.return_value = notice_data
        result = schematize_opp(self.opp[0])
        expected = {**required_data, **notice_data}
        self.assertEqual(result, expected)

    def test_naics_filter(self):
        #opps = [{'data':{'naics': [{'code': ['123','33435']}]}}, #keep
        #        {'data':{'naics': [{'code': ['123', '1234']}]}},
        #        {'data':{'naics': [{'code': ['33435']}]}},
        #        {'data':{'naics': [{'code': ['123']}]}}]

        #opps = [{'naics': [{'code': ['123','33435']}]}, #keep
        #        {'naics': [{'code': ['123', '1234']}]},
        #        {'naics': [{'code': ['33435']}]},
        #        {'naics': [{'code': ['123']}]}]

        opps = [{'naics': [{'code': '33435'}]},
                {'naics': [{'code': '123'}]}]

        result = naics_filter(opps)
        #expected = [{'data': {'naics': [{'code': ['123','33435']}]}},
        #            {'data': {'naics': [{'code': ['33435']}]}}]

        expected = [{'naics': [{'code': '33435'}]}]

        self.assertEqual(result, expected)

    def test_get_dates_from_opp(self):
        opp = {'modifiedDate': '2019-09-19T21:18:20.669+0000',
               'publishDate': '2019-09-19T21:18:20.669+0000'}
        result = get_dates_from_opp(opp)
        expected = (dt.strptime('2019-09-19', "%Y-%m-%d"),
                    dt.strptime('2019-09-19', "%Y-%m-%d"))
        self.assertEqual(result, expected)
    
    def test_get_dates_from_opp_diff_fmt(self):
        opp = {'modifiedDate': '2019-09-19 00:00:00',
               'publishDate': '2019-09-19 00:00:00'}
        result = get_dates_from_opp(opp)
        expected = (dt.strptime('2019-09-19', "%Y-%m-%d"),
                    dt.strptime('2019-09-19', "%Y-%m-%d"))
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_mod_only(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19T21:18:20.669+0000'},
                {'modifiedDate': '2019-09-18T21:18:20.669+0000'},
                {'modifiedDate': '2019-09-17T21:18:20.669+0000'}]
        result = find_yesterdays_opps(opps)
        expected = ([{'modifiedDate': '2019-09-18T21:18:20.669+0000'}],
                    False)
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_mod_and_post(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-17 00:00:00', 'publishDate':'2019-09-17 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([{'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-19 00:00:00'}],
                    False)
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_mod_and_post(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-17 00:00:00', 'publishDate':'2019-09-17 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([{'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-19 00:00:00'}],
                    False)
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_post_only(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-18 00:00:00'},
                {'modifiedDate': '2019-09-17 00:00:00', 'publishDate':'2019-09-17 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-18 00:00:00'}],
                    False)
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_only_today(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-14 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([],
                    True)
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_more(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-14 00:00:00'},
                {'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-13 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([{'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-14 00:00:00'},
                     {'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-13 00:00:00'}],
                    True)
        self.assertEqual(result, expected)

    @patch('utils.sam_utils.get_day')
    def test_find_yesterdays_opps_no_more(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-17 00:00:00', 'publishDate':'2019-09-17 00:00:00'},
                {'modifiedDate': '2019-09-14 00:00:00', 'publishDate':'2019-09-14 00:00:00'},
                {'modifiedDate': '2019-09-12 00:00:00', 'publishDate':'2019-09-11 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([],
                    False)
        self.assertEqual(result, expected)


    def test_api_pagination(self):
        uri, params, headers = get_opp_request_details()
        params['postedFrom'] = '01/26/2020'
        params['postedTo'] = '01/26/2020'
        params['limit'] = 10
        params['page'] = 0

        # dict of opportunites - Page 1
        opps, total_pages = get_opps(uri, params, headers)
        self.assertGreater(total_pages, 1)

        # dict of opportunites - Page 2
        params.update({'page': 1})
        opps_2, total_pages_2 = get_opps(uri, params, headers)
        self.assertGreater(total_pages_2, 1)
        self.assertNotEqual(opps[0]['_id'], opps_2[0]['_id'], "We should get different notice IDs on different pages, instead got {} and {}".format(opps[0]['_id'], opps_2[0]['_id']) )




if __name__ == '__main__':
    unittest.main()