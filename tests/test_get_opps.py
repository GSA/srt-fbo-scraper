import os
import shutil
import sys
import unittest

from unittest.mock import patch, MagicMock
from addict import Addict
import tempfile
import requests

import requests_mock

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from tests import mock_opps
from tests.test_utils import get_zip_in_memory
from fbo_scraper.get_opps import get_opps_for_day, get_docs, get_attachment_data, \
                           transform_opps, schematize_opp
from tests.mock_opps import mock_opp_one

TEST_DIR = os.path.dirname(os.path.realpath(__file__))

class GetOppsTestCase(unittest.TestCase):

    def setUp(self):
        self.zip_in_memory = get_zip_in_memory()
        self.out_path =  tempfile.mkdtemp()
        # Copying data from /tests/data to out_path
        test_data_path = os.path.join(TEST_DIR, 'data')
        self.api_key = os.environ.get('SAM_API_KEY')

        for filename in os.listdir(test_data_path):
            shutil.copy2(os.path.join(test_data_path, filename), self.out_path)

        self.beta_opp_uri = 'https://api.sam.gov/prod/opportunity/v1/api/search'
        self.mock_schematized_opp_one = mock_opps.mock_schematized_opp_one
        self.maxDiff = None
        
    def tearDown(self):
        self.zip_in_memory = None
        if os.path.exists(self.out_path):
            shutil.rmtree(self.out_path)
        self.out_path = None
        self.beta_opp_uri = None
        self.mock_schematized_opp_one

    @patch('fbo_scraper.get_opps.get_opportunities_search_url', return_value = 'https://api.sam.gov/prod/opportunity/v1/api/search')
    @patch('fbo_scraper.get_opps.requests_retry_session')
    def test_get_opps_for_day(self, mock_session, mock_search_url):
        mock_search_url.return_value = 'https://api.sam.gov/prod/opportunity/v1/api/search' 
        
        # Set up mock response data
        mock_response_data = {
            'totalRecords': 2,
            'opportunitiesData': [
                {
                    'postedDate': '2022-01-01',
                    'solicitationNumber': 'ABC123',
                    'title': 'Test Opportunity 1',
                    'active': 'true'
                },
                {
                    'postedDate': '2022-01-02',
                    'solicitationNumber': 'DEF456',
                    'title': 'Test Opportunity 2',
                    'active': 'true'
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response

        # Call the function with mock data
        opps = get_opps_for_day(limit=1)

        # Check the results
        self.assertEqual(len(opps), 1)
        self.assertEqual(opps[0]['solicitationNumber'], 'ABC123')

    @patch('fbo_scraper.get_opps.get_opportunities_search_url', return_value = 'https://api.sam.gov/prod/opportunity/v1/api/search')
    @patch('fbo_scraper.get_opps.requests_retry_session')
    def test_get_opps_for_day_error(self, mock_session, mock_search_url):
        from fbo_scraper.get_opps import SamApiError
        mock_search_url.return_value = 'https://api.sam.gov/prod/opportunity/v1/api/search' 
        
        # Set up mock response data
        mock_response_data = {
            "error": {
                "code": "API_KEY_INVALID",
                "message": "An invalid API key was supplied. Please submit with a valid API key."
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 403
        mock_session.return_value.get.return_value = mock_response

        # Call the function with mock data
        with self.assertRaises(SamApiError) as context:
            opps = get_opps_for_day(limit=1)

        # Check the results
        self.assertTrue('Sam.gov API returned error message' in str(context.exception))

    @patch('fbo_scraper.get_opps.make_attachment_request', return_value = MagicMock(headers={'Content-Disposition': 'attachment; filename=test.pdf'}))
    @patch('fbo_scraper.get_opps.shutil.copyfileobj')
    @requests_mock.Mocker()
    def test_get_docs(self, m_make_attachment_request, m_copy_file, mock_request):
        opp_id = 'test'
        url = f'https://api.sam.gov/prod/opportunity/v1/api/{opp_id}/resources/download/zip'
        
        opp = dict(resourceLinks=[url])

        mock_request.register_uri('GET',
                                  url = url,
                                  status_code = 200)
        
        result = get_docs(opp, self.out_path)
        m_copy_file.assert_called_once()

        expected = [(os.path.join(self.out_path, 'test.pdf'), url)]
        self.assertEqual(result, expected)

    @patch('fbo_scraper.get_opps.get_doc_text')
    def test_get_attachment_data(self, mock_get_doc_text):
        mock_get_doc_text.return_value = 'test'
        url = 'test'
        result = get_attachment_data('test.txt', url)
        expected = mock_opps.mock_attachment_data
        self.assertEqual(result, expected)
    
    @patch('fbo_scraper.get_opps.get_attachment_data')
    @patch('fbo_scraper.get_opps.get_doc_text')    
    @patch('fbo_scraper.get_opps.get_docs')
    @patch('fbo_scraper.get_opps.schematize_opp')
    def test_transform_opps(self, m_schematize_opp, m_g_docs, m_g_doc_text, m_g_attachment_data):
        m_schematize_opp.return_value = self.mock_schematized_opp_one
        m_g_docs.return_value = ['test.pdf']
        m_g_doc_text.return_value = 'test'
        m_g_attachment_data.return_value = mock_opps.mock_attachment_data
        result = transform_opps([mock_opps.mock_opp_one[0]], self.out_path)
        # repeat 3 times since opps has three records
        expected = [mock_opps.mock_transformed_opp_one]
        self.assertEqual(result, expected)

    @patch('fbo_scraper.get_opps.schematize_opp')
    def test_transform_opps_duplicates(self, m_schematize_opp):
        m_schematize_opp.return_value = mock_opps.mock_schematized_solnum_constraint_error[0]
        result = transform_opps(mock_opps.mock_schematized_solnum_constraint_error, self.out_path, skip_attachments=True)
        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()