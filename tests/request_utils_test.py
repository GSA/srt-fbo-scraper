import os
import sys
import unittest
import requests_mock
import re

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.request_utils import requests_retry_session, get_opp_request_details, get_opps, \
    get_doc_request_details, get_org_request_details
from utils.predict import Predict
from tests.mock_opps import mock_transformed_opp_bad_attachment, mock_transformed_opp_one
from unittest.mock import MagicMock, Mock

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

    def test_get_opps(self):
        uri = 'https://www.example.com'
        response_json = {'_embedded': { 'results' :[{'test':'data'}]},
                    'page': {'totalPages':1}}
        response_mock = MagicMock()
        response_mock.json = Mock(return_value =response_json)
        session_mock = MagicMock()
        session_mock.get = Mock(return_value = response_mock )

        expected = get_opps(uri, {}, {},session_mock)
        result = ([{'test':'data'}],1)
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


    def test_bad_attachment_detection(self):
        # bad data should get an ERROR log message
        predict = Predict(data = [mock_transformed_opp_bad_attachment])
        with self.assertLogs( level='ERROR') as a:
            predict.insert_predictions()
            msgFound = False
            for msg in a.output:
                if re.match(".*suspicious attachment.*", msg):
                    msgFound = True
            assert msgFound

        # good data should just have INFO logging
        predict = Predict(data = [mock_transformed_opp_one])
        with self.assertLogs(level='INFO'):
            predict.insert_predictions()


if __name__ == '__main__':
    unittest.main()