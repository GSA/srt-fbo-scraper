import os
import sys
import unittest
from unittest.mock import patch

import responses
import requests_mock

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.request_utils import requests_retry_session, get_opp_request_details, get_opps, \
    get_doc_request_details, get_org_request_details
import tests.mock_opps

class RequestUtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.params = {'cancelled': False, 
                       'noticeType': 'o,p,k,r',
                       'size': '100',
                       'sortBy': '-modifiedOn'}
        
    def tearDown(self):
        self.params = None

    def test_requests_retry_session(self):
        with requests_retry_session() as session:
            r = session.get('https://www.example.com')
        self.assertTrue(r)

    def test_get_doc_request_details_alpha(self):
        opp_id = '123'
        try:
            os.environ["ALPHA_SAM_API_KEY"] = "alpha"
            os.environ['SAM_AUTHORIZER'] = 'foo'
            uri = f'https://api-alpha.sam.gov/prodlike/opportunity/v1/api/{opp_id}/resources/download/zip'
            self.params.update({'api_key': "alpha"})
            headers = {'Authorization': 'foo'}
            result = get_doc_request_details(opp_id)
            expected = (uri, self.params, headers)
            self.assertTrue(result, expected)
        finally:
            del os.environ["ALPHA_SAM_API_KEY"]
    
    def test_get_doc_request_details_beta(self):
        opp_id = '123'
        try:
            os.environ["BETA_SAM_API_KEY"] = "beta"
            os.environ['SAM_AUTHORIZER'] = 'foo'
            uri = f'https://api.sam.gov/prod/opportunity/v1/api/{opp_id}/resources/download/zip'
            self.params.update({'api_key': "alpha"})
            headers = {'Authorization': 'foo'}
            result = get_doc_request_details(opp_id)
            expected = (uri, self.params, headers)
            self.assertTrue(result, expected)
        finally:
            del os.environ["BETA_SAM_API_KEY"]

    def test_get_opp_request_details_alpha(self):
        try:
            os.environ["ALPHA_SAM_API_KEY"] = "alpha"
            os.environ['SAM_AUTHORIZER'] = 'bar'
            uri = 'https://api-alpha.sam.gov/prodlike/opportunity/v1/api/search'
            self.params.update({'api_key': "beta"})
            headers = {'Authorization': 'bar'}
            result = get_opp_request_details()
            expected = (uri, self.params, headers)
            self.assertTrue(result, expected)
        finally:
            del os.environ["ALPHA_SAM_API_KEY"]
    
    def test_get_opp_request_details_beta(self):
        try:
            os.environ["BETA_SAM_API_KEY"] = "beta"
            os.environ['SAM_AUTHORIZER'] = 'bar'
            uri = 'https://api.sam.gov/prod/opportunity/v1/api/search'
            self.params.update({'api_key': "beta"})
            headers = {'Authorization': 'bar'}
            result = get_opp_request_details()
            expected = (uri, self.params, headers)
            self.assertTrue(result, expected)
        finally:
            del os.environ["BETA_SAM_API_KEY"]

    @requests_mock.Mocker()
    def test_get_opps(self, mock_request):
        uri = 'https://www.example.com'
        response = {'_embedded': {'opportunity': 'test'},
                    'page': {'totalPages': '1'}}
        mock_request.register_uri('GET',
                                  url = uri,
                                  json = response,
                                  status_code = 200)
        expected = get_opps(uri, {}, {})
        result = ('test','1')
        self.assertEqual(result, expected)

    def test_get_org_request_details(self):
        try:
            os.environ["BETA_SAM_API_KEY_PUB"] = "pub"
            uri = 'https://api-alpha.sam.gov/prodlike/federalorganizations/v1/orgs'
            params = {'api_key': "pub"}
            result = get_org_request_details()
            expected = (uri, params)
            self.assertTrue(result, expected)
        finally:
            del os.environ["BETA_SAM_API_KEY_PUB"]

if __name__ == '__main__':
    unittest.main()