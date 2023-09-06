import pytest
from datetime import datetime as dt
import os
import shutil
import sys
import unittest
from unittest.mock import patch
import copy


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.test_utils import get_zip_in_memory, get_day_side_effect
from tests import mock_opps
from fbo_scraper.sam_utils import (write_zip_content, get_notice_data, get_notice_type,
                            schematize_opp, naics_filter, get_dates_from_opp, find_yesterdays_opps)


class SamUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.zip_in_memory = get_zip_in_memory()
        self.opp = mock_opps.mock_opp_one[0]
        self.maxDiff = None

    def tearDown(self):
        self.zip_in_memory = None
        self.opp = None


    def test_write_zip_content(self):    
        content = self.zip_in_memory
        try:
            result = write_zip_content(content, "temp_archive")
            expected = ["temp_archive/test.pdf"]
            self.assertEqual(result, expected)
        finally:
            file_to_delete = os.path.join(os.getcwd(), "attachments", "test.pdf")
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
            if os.path.exists("temp_archive"):
                shutil.rmtree("temp_archive")

    def test_get_notice_data(self):
        # Set up mock data
        mock_opp_data = {
            'pointOfContact': [
                {'email': 'test1@example.com'},
                {'email': 'test2@example.com'}
            ],
            'classificationCode': 'ABC',
            'naicsCode': '123',
            'title': 'test opportunity',
            'uiLink': 'https://example.com',
            'typeOfSetAside': 'Small Business Set-Aside'
        }
        mock_opp_id = 'ABC123'

        # Call the function with mock data
        notice_data = get_notice_data(mock_opp_data, mock_opp_id)

        # Check the results
        self.assertIsNotNone(notice_data)
        self.assertEqual(notice_data['classcod'], 'ABC')
        self.assertEqual(notice_data['psc'], 'ABC')
        self.assertEqual(notice_data['naics'], '123')
        self.assertEqual(notice_data['subject'], 'Test Opportunity')
        self.assertEqual(notice_data['url'], 'https://example.com')
        self.assertEqual(notice_data['setaside'], 'Small Business Set-Aside')
        self.assertEqual(notice_data['emails'], ['test1@example.com', 'test2@example.com'])

    def test_get_notice_type_presol(self):
        expected = get_notice_type("p")
        result = "Presolicitation"
        self.assertEqual(result, expected)

    def test_get_notice_type_combine(self):
        expected = get_notice_type("k")
        result = "Combined Synopsis/Solicitation"
        self.assertEqual(result, expected)

    def test_get_notice_type_sol(self):
        expected = get_notice_type("o")
        result = "Solicitation"
        self.assertEqual(result, expected)

    def test_get_notice_type_no_match(self):
        expected = get_notice_type("u")
        result = None
        self.assertEqual(result, expected)

    def test_schematize_opp(self):
        # Set up mock data
        mock_opp = {
            'solicitationNumber': 'ABC123',
            'type': 'Presolicitation',
            'fullParentPathName': 'Department of Defense.Air Force'
        }

        # Call the function with mock data
        schematized_opp = schematize_opp(mock_opp)

        # Check the results
        self.assertIsNotNone(schematized_opp)
        self.assertEqual(schematized_opp['opp_id'], 'ABC123')
        self.assertEqual(schematized_opp['notice type'], 'Presolicitation')
        self.assertEqual(schematized_opp['agency'], 'Department of Defense')
        self.assertEqual(schematized_opp['office'], 'Air Force')
        self.assertEqual(schematized_opp['compliant'], 0)
        self.assertEqual(schematized_opp['attachments'], [])

    def test_schematize_opp_with_errors(self):
        opp = copy.deepcopy(self.opp)
        # use only one level of hierarchy to make sure the schematize function can handle it
        opp['fullParentPathName'] = "test"
        result = schematize_opp(opp)
        self.assertEqual(result['agency'], "test")
        self.assertEqual(result['office'], "")



    def test_naics_filter(self):
        # opps = [{'data':{'naics': [{'code': ['123','33435']}]}}, #keep
        #        {'data':{'naics': [{'code': ['123', '1234']}]}},
        #        {'data':{'naics': [{'code': ['33435']}]}},
        #        {'data':{'naics': [{'code': ['123']}]}}]

        # opps = [{'naics': [{'code': ['123','33435']}]}, #keep
        #        {'naics': [{'code': ['123', '1234']}]},
        #        {'naics': [{'code': ['33435']}]},
        #        {'naics': [{'code': ['123']}]}]

        opps = [{"naics": [{"code": "33435"}]}, {"naics": [{"code": "123"}]}]

        result = naics_filter(opps)
        # expected = [{'data': {'naics': [{'code': ['123','33435']}]}},
        #            {'data': {'naics': [{'code': ['33435']}]}}]

        expected = [{"naics": [{"code": "33435"}]}]

        self.assertEqual(result, expected)

    def test_get_dates_from_opp(self):
        opp = {
            "modifiedDate": "2019-09-19T21:18:20.669+0000",
            "publishDate": "2019-09-19T21:18:20.669+0000",
        }
        result = get_dates_from_opp(opp)
        expected = (
            dt.strptime("2019-09-19", "%Y-%m-%d"),
            dt.strptime("2019-09-19", "%Y-%m-%d"),
        )
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_mod_only(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [
            {"modifiedDate": "2019-09-19T21:18:20.669+0000"},
            {"modifiedDate": "2019-09-18T21:18:20.669+0000"},
            {"modifiedDate": "2019-09-17T21:18:20.669+0000"},
        ]
        result = find_yesterdays_opps(opps)
        expected = ([{"modifiedDate": "2019-09-18T21:18:20.669+0000"}], False)
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_mod_and_post(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [
            {
                "modifiedDate": "2019-09-19 00:00:00",
                "publishDate": "2019-09-19 00:00:00",
            },
            {
                "modifiedDate": "2019-09-18 00:00:00",
                "publishDate": "2019-09-19 00:00:00",
            },
            {
                "modifiedDate": "2019-09-17 00:00:00",
                "publishDate": "2019-09-17 00:00:00",
            },
        ]
        result = find_yesterdays_opps(opps)
        expected = (
            [
                {
                    "modifiedDate": "2019-09-18 00:00:00",
                    "publishDate": "2019-09-19 00:00:00",
                }
            ],
            False,
        )
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_mod_and_post(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [{'modifiedDate': '2019-09-19 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-19 00:00:00'},
                {'modifiedDate': '2019-09-17 00:00:00', 'publishDate':'2019-09-17 00:00:00'}]
        result = find_yesterdays_opps(opps)
        expected = ([{'modifiedDate': '2019-09-18 00:00:00', 'publishDate':'2019-09-19 00:00:00'}],
                    False)
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_post_only(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [
            {
                "modifiedDate": "2019-09-19 00:00:00",
                "publishDate": "2019-09-19 00:00:00",
            },
            {
                "modifiedDate": "2019-09-19 00:00:00",
                "publishDate": "2019-09-18 00:00:00",
            },
            {
                "modifiedDate": "2019-09-17 00:00:00",
                "publishDate": "2019-09-17 00:00:00",
            },
        ]
        result = find_yesterdays_opps(opps)
        expected = (
            [
                {
                    "modifiedDate": "2019-09-19 00:00:00",
                    "publishDate": "2019-09-18 00:00:00",
                }
            ],
            False,
        )
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_only_today(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [
            {
                "modifiedDate": "2019-09-19 00:00:00",
                "publishDate": "2019-09-19 00:00:00",
            },
            {
                "modifiedDate": "2019-09-19 00:00:00",
                "publishDate": "2019-09-14 00:00:00",
            },
        ]
        result = find_yesterdays_opps(opps)
        expected = ([], True)
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_more(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [
            {
                "modifiedDate": "2019-09-19 00:00:00",
                "publishDate": "2019-09-19 00:00:00",
            },
            {
                "modifiedDate": "2019-09-18 00:00:00",
                "publishDate": "2019-09-14 00:00:00",
            },
            {
                "modifiedDate": "2019-09-18 00:00:00",
                "publishDate": "2019-09-13 00:00:00",
            },
        ]
        result = find_yesterdays_opps(opps)
        expected = (
            [
                {
                    "modifiedDate": "2019-09-18 00:00:00",
                    "publishDate": "2019-09-14 00:00:00",
                },
                {
                    "modifiedDate": "2019-09-18 00:00:00",
                    "publishDate": "2019-09-13 00:00:00",
                },
            ],
            True,
        )
        self.assertEqual(result, expected)

    @patch('fbo_scraper.sam_utils.get_day')
    def test_find_yesterdays_opps_no_more(self, mock_get_day):
        mock_get_day.side_effect = get_day_side_effect
        opps = [
            {
                "modifiedDate": "2019-09-17 00:00:00",
                "publishDate": "2019-09-17 00:00:00",
            },
            {
                "modifiedDate": "2019-09-14 00:00:00",
                "publishDate": "2019-09-14 00:00:00",
            },
            {
                "modifiedDate": "2019-09-12 00:00:00",
                "publishDate": "2019-09-11 00:00:00",
            },
        ]
        result = find_yesterdays_opps(opps)
        expected = ([], False)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
