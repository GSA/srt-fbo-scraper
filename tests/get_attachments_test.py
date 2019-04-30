import unittest
from unittest.mock import patch, Mock
import sys
import responses
from datetime import datetime
import requests_mock
import requests
import json
import os
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils import get_attachments
from fixtures import get_attachments_fixtures


class GetAttachmentsTestCase(unittest.TestCase):

    def setUp(self):
        self.attachments_get_expected = get_attachments_fixtures.attachments_get_expected
    
    def tearDown(self):
        self.attachments_get_expected = None

    @requests_mock.Mocker()
    def test_attachments_get(self, mock_request):
        uri = 'https://api.sam.gov/prod/opps/v1/opportunities/attachments'
        mock_request.register_uri('GET',
                                  url = uri,
                                  json = self.attachments_get_expected,
                                  status_code = 200,
                                  complete_qs = False)
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        solicitation_number = 'dhsindustrydaynaics111120'
        result = get_attachments.attachments_get(notice_id, solicitation_number)
        expected = self.attachments_get_expected
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_attachments_get_404(self, mock_request):
        uri = 'https://api.sam.gov/prod/opps/v1/opportunities/attachments'
        mock_request.register_uri('GET',
                                  url = uri,
                                  status_code = 404,
                                  complete_qs = False)
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        solicitation_number = 'dhsindustrydaynaics111120'
        result = get_attachments.attachments_get(notice_id, solicitation_number)
        expected = None
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_attachments_get_exc(self, mock_request):
        uri = 'https://api.sam.gov/prod/opps/v1/opportunities/attachments'
        mock_request.register_uri('GET',
                                  url = uri,
                                  exc = requests.exceptions.ConnectTimeout,
                                  complete_qs = False)
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        solicitation_number = 'dhsindustrydaynaics111120'
        result = get_attachments.attachments_get(notice_id, solicitation_number)
        expected = None
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_cookies(self, mock_request):
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        uri = f'https://beta.sam.gov/opp/{notice_id}'
        cookies = {'citrix_ns_id':'foo',
                   'citrix_ns_id_.sam.gov_%2F_wlf': 'bar'}
        mock_request.register_uri('GET',
                                  url = uri,
                                  status_code = 200,
                                  complete_qs = False,
                                  cookies = cookies)
        result = get_attachments.get_notice_cookies(uri)
        expected = 'citrix_ns_id=foo; citrix_ns_id_.sam.gov_%2F_wlf=bar'
        self.assertEqual(result, expected)
    
    @requests_mock.Mocker()
    @patch('utils.get_attachments.get_notice_cookies')
    def test_get_notice_file(self, mock_request, mock_get_notice_cookies):
        cookies = 'citrix_ns_id=foo; citrix_ns_id_.sam.gov_%2F_wlf=bar'
        mock_get_notice_cookies.return_value = cookies
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        resource_id = '311a684a24598c551b9df4492ffa8d47'
        uri = f'https://api.sam.gov/prod/opps/v1/opportunities/resources/files/{resource_id}'
        mock_request.register_uri('GET',
                                  url = uri,
                                  status_code = 200,
                                  content = b'fizzbuzz',
                                  complete_qs = False,
                                  cookies = cookies)
        result = get_attachments.get_notice_file(notice_id, resource_id)
        expected = (b'fizzbuzz', uri)
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    @patch('utils.get_attachments.get_notice_cookies')
    def test_get_notice_file_404(self, mock_request, mock_get_notice_cookies):
        cookies = 'citrix_ns_id=foo; citrix_ns_id_.sam.gov_%2F_wlf=bar'
        mock_get_notice_cookies.return_value = cookies
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        resource_id = '311a684a24598c551b9df4492ffa8d47'
        uri = f'https://api.sam.gov/prod/opps/v1/opportunities/resources/files/{resource_id}'
        mock_request.register_uri('GET',
                                  url = uri,
                                  status_code = 404,
                                  complete_qs = False,
                                  cookies = cookies)
        result = get_attachments.get_notice_file(notice_id, resource_id)
        expected = (None, uri)
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    @patch('utils.get_attachments.get_notice_cookies')
    def test_get_notice_file_exc(self, mock_request, mock_get_notice_cookies):
        cookies = 'citrix_ns_id=foo; citrix_ns_id_.sam.gov_%2F_wlf=bar'
        mock_get_notice_cookies.return_value = cookies
        notice_id = 'a07312cf5c502b093d57be0924d6e89e'
        resource_id = '311a684a24598c551b9df4492ffa8d47'
        uri = f'https://api.sam.gov/prod/opps/v1/opportunities/resources/files/{resource_id}'
        mock_request.register_uri('GET',
                                  url = uri,
                                  exc = requests.exceptions.ConnectTimeout,
                                  complete_qs = False)
        result = get_attachments.get_notice_file(notice_id, resource_id)
        expected = (None, uri)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()