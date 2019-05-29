import unittest
from unittest.mock import patch, Mock
import sys
import warnings
from datetime import datetime
import json
import os

import responses
import requests_mock
import requests

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils import get_notices
from fixtures import get_notices_fixtures

class GetNoticesTestCase(unittest.TestCase):

    def setUp(self):
        self.search_json = get_notices_fixtures.search_api_json
        self.schematize_results_expected = get_notices_fixtures.schematize_results_expected
    
    def tearDown(self):
        self.search_json = None
        self.schematize_results_expected = None

    def test_xstr_none(self):
        result = get_notices.xstr(None)
        expected = ''
        self.assertEqual(result, expected)

    def test_xstr_int(self):
        result = get_notices.xstr(123)
        expected = '123'
        self.assertEqual(result, expected)

    def test_xstr_str(self):
        result = get_notices.xstr('123')
        expected = '123'
        self.assertEqual(result, expected)

    def test_get_random(self):
        #simply test if it can be called without raising an error
        try:
            get_notices.get_random()
        except Exception as e:
            self.fail(f"get_random() raised {e} unexpectedly!")
        self.assertTrue(True)

    @patch('utils.get_notices.datetime')
    def test_get_now_minus_n(self, now_mock):
        now_mock.utcnow = Mock(return_value = datetime(2019, 4, 29, 10, 20, 53, 532205)) 
        result = get_notices.get_now_minus_n(1)
        expected = '2019-04-28-04:00'
        self.assertEqual(result, expected)
    
    @requests_mock.Mocker()
    def test_api_get(self, mock_request):
        uri = 'https://www.api.test.gov/search/?page=0'
        payload = {'page':'0'}
        mock_request.register_uri('GET',
                                  url = uri,
                                  json = self.search_json,
                                  status_code = 200,
                                  complete_qs = False)
        result = get_notices.api_get(uri, payload)
        expected = self.search_json
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_api_get_exc(self, mock_request):
        uri = 'https://www.api.test.gov/search/?page=0'
        payload = {'page':'0'}
        mock_request.register_uri('GET',
                                  url = uri,
                                  exc = requests.exceptions.ConnectTimeout,
                                  complete_qs = False)
        result = get_notices.api_get(uri, payload)
        expected = None
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_api_get_404(self, mock_request):
        uri = 'https://www.api.test.gov/search/?page=0'
        payload = {'page':'0'}
        mock_request.register_uri('GET',
                                  url = uri,
                                  status_code = 404,
                                  complete_qs = False)
        result = get_notices.api_get(uri, payload)
        expected = None
        self.assertEqual(result, expected)

    @patch('utils.get_notices.api_get')
    def test_get_opportunities(self, mock_api_get):
        mock_api_get.return_value = self.search_json
        result = get_notices.get_opportunities()
        expected = self.search_json['_embedded']['results']
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_opportunities_two_pages(self, mock_request):
        uri = 'https://api.sam.gov/prod/sgs/v1/search/'
        search_json = self.search_json
        search_json['page']['totalPages'] = 2
        mock_request.register_uri('GET',
                                  url = uri,
                                  json = search_json,
                                  status_code = 200,
                                  complete_qs = False)
        result = get_notices.get_opportunities()
        expected = self.search_json['_embedded']['results']
        expected.extend(expected)
        self.assertEqual(result, expected)

    def test_get_date_and_year(self):
        result = get_notices.get_date_and_year("2008-10-28T13:03:28-04:00")
        expected = ('1028', '08')
        self.assertEqual(result, expected)

    def test_proper_case(self):
        result = get_notices.proper_case('DEPARTMENT OF HOUSING AND URBAN DEVELOPMENT')
        expected = 'Department of Housing and Urban Development'
        self.assertEqual(result, expected)

    def test_parse_agency_name(self):
        #not patching proper_case() here
        result = get_notices.parse_agency_name('HOMELAND SECURITY, DEPARTMENT OF')
        expected = 'Department of Homeland Security'
        self.assertEqual(result, expected)

    def test_get_agency_office_location_zip_offadd(self):
        organization_hierarchy = self.search_json['_embedded']['results'][0]['organizationHierarchy']
        result = get_notices.get_agency_office_location_zip_offadd(organization_hierarchy)
        expected = ('Department of Homeland Security', 'Office of Procurement Operations', 'Office of Procurement Operations', '','')
        self.assertEqual(result, expected)

    def test_get_classcod_naics(self):
        psc_naics = self.search_json['_embedded']['results'][0]['psc']
        result = get_notices.get_classcod_naics(psc_naics)
        expected = '99'
        self.assertEqual(result, expected)

    def test_get_classcod_naics_none(self):
        #test where None types are values
        psc_naics = [{'code': 'L', 'id': 4150, 'value': 'TECHNICAL REPRESENTATIVE SVCS.'}, 
                     {'code': None, 'id': None, 'value': None}]
        result = get_notices.get_classcod_naics(psc_naics)
        expected = 'L' 
        self.assertEqual(result, expected)

    def test_get_respdate(self):
        response_date = "2019-04-16T15:00:00-04:00"
        result = get_notices.get_respdate(response_date)
        expected = '041619'
        self.assertEqual(result, expected)

    def test_get_contact(self):
        point_of_contacts = self.search_json['_embedded']['results'][0]['pointOfContacts']
        result = get_notices.get_contact(point_of_contacts)
        expected = 'Fizz Buzz, Contracting Officer, 202-447-5543'
        self.assertEqual(result, expected)

    def test_get_contact_multiple(self):
        point_of_contacts = [{'lastName': 'Buzz',
                              'firstName': 'Fizz',
                              'phone': '202-447-5543',
                              'fullName': 'Fizz Buzz',
                              'fax': '202-555-5555',
                              'type': 'primary',
                              'title': 'Contracting Officer',
                              'email': 'foo.bar@dhs.gov'},
                             {'lastName': 'Bar',
                              'firstName': 'Foo',
                              'phone': '202-447-5543',
                              'fullName': 'Foo Bar',
                              'fax': '202-555-5555',
                              'type': 'primary',
                              'title': 'Contracting Officer',
                              'email': 'foo.bar@dhs.gov'}]
        result = get_notices.get_contact(point_of_contacts)
        expected = 'Fizz Buzz, Contracting Officer, 202-447-5543; Foo Bar, Contracting Officer, 202-447-5543'
        self.assertEqual(result, expected)

    def test_get_contact_missing_values(self):
        point_of_contacts = [{'lastName': None,
                              'firstName': None,
                              'phone': '202-447-5543',
                              'fullName': None,
                              'fax': '202-555-5555',
                              'type': 'primary',
                              'title': 'Contracting Officer',
                              'email': 'foo.bar@dhs.gov'},
                             ]
        result = get_notices.get_contact(point_of_contacts)
        expected = ''
        self.assertEqual(result, expected)

    def test_get_contact_partially_missing_values(self):
        point_of_contacts = [{'lastName': None,
                              'firstName': None,
                              'phone': '202-447-5543',
                              'fullName': None,
                              'fax': '202-555-5555',
                              'type': 'primary',
                              'title': 'Contracting Officer',
                              'email': 'foo.bar@dhs.gov'},
                              {'lastName': 'Foo',
                              'firstName': 'Bar',
                              'phone': '202-447-5543',
                              'fullName': 'Foo Bar',
                              'fax': '202-555-5555',
                              'type': 'primary',
                              'title': 'Contracting Officer',
                              'email': 'foo.bar@dhs.gov'}
                             ]
        result = get_notices.get_contact(point_of_contacts)
        expected = 'Foo Bar, Contracting Officer, 202-447-5543'
        self.assertEqual(result, expected)

    def test_get_description(self):
        descriptions = [{'lastModifiedDate': '2008-10-28T13:03:28-04:00',
                         'content': 'this is the earlier and wrong description'},
                        {'lastModifiedDate': '2009-10-28T13:03:28-04:00',
                         'content': '<title>test123</title>'}]
        result = get_notices.get_description(descriptions)
        expected = '<title>test123</title>'
        self.assertEqual(result, expected)

    def test_get_description_no_date(self):
        descriptions = [{'otherDate': '2008-10-28T13:03:28-04:00',
                         'content': 'this is the longer and correct description'},
                        {'otherDate': '2009-10-28T13:03:28-04:00',
                         'content': '<title>test123</title>'}]
        result = get_notices.get_description(descriptions)
        expected = 'this is the longer and correct description'
        self.assertEqual(result, expected)

    def test_get_text_from_html(self):
        result = get_notices.get_text_from_html('<title>test123</title>')
        expected = 'test123'
        self.assertEqual(result, expected)

    def test_get_text_from_html_none(self):
        result = get_notices.get_text_from_html('')
        expected = ''
        self.assertEqual(result, expected)

    def test_get_setasides(self):
        setasides = {'value': 'foo'}
        result = get_notices.get_setasides(setasides)
        expected = 'foo'
        self.assertEqual(result, expected)
    
    def test_get_setasides_list(self):
        setasides = [{'value': 'foo'},
                     {'value': 'bar'}]
        result = get_notices.get_setasides(setasides)
        expected = 'foo bar'
        self.assertEqual(result, expected)

    def test_get_setasides_none(self):
        setasides = None
        result = get_notices.get_setasides(setasides)
        expected = 'N/A'
        self.assertEqual(result, expected)

    def test_get_place_of_performance(self):
        place_of_performance = [{'city': "Washington",
                                 'country': "US",
                                 'state': "DC",
                                 'streetAddress': "1800 F Street, NW",
                                 'streetAddress2': None,
                                 'zip': "20006"}]
        result = get_notices.get_place_of_performance(place_of_performance)
        expected = ('20006', 
                    'US', 
                    "1800 F Street, NW Washington, DC")
        self.assertEqual(result, expected)

    def test_extract_emails(self):
        res = self.search_json['_embedded']['results'][0]
        result = get_notices.extract_emails(res)
        expected = ['foo.bar@dhs.gov']
        self.assertCountEqual(result, expected)

    def test_schematize_results(self):
        results = self.search_json['_embedded']['results']
        result = get_notices.schematize_results(results)
        expected = self.schematize_results_expected
        self.assertCountEqual(result, expected)

    def test_get_notices(self):
        #end-to-end test
        results = get_notices.get_notices(modified_date = '2019-01-03')
        result = sum(len(v) for k,v in results.items())
        expected = 3
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
