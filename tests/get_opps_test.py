import os
import shutil
import sys
import unittest
from unittest.mock import patch

import requests_mock

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from tests import mock_opps
from tests.test_utils import get_zip_in_memory
from utils.get_opps import get_yesterdays_opps, get_docs, get_attachment_data, \
                           transform_opps, schematize_opp
from tests.mock_opps import mock_opp_one

class GetOppsTestCase(unittest.TestCase):

    def setUp(self):
        self.zip_in_memory = get_zip_in_memory()
        self.out_path = 'attachments'
        self.beta_opp_uri = 'https://api.sam.gov/prod/opportunity/v1/api/search'
        self.mock_schematized_opp_one = mock_opps.mock_schematized_opp_one
        #self.maxDiff = None
        
    def tearDown(self):
        self.zip_in_memory = None
        if os.path.exists(self.out_path):
            shutil.rmtree(self.out_path)
        self.out_path = None
        self.beta_opp_uri = None
        self.mock_schematized_opp_one
    
    @patch('utils.get_opps.find_yesterdays_opps')
    @patch('utils.get_opps.get_opps')
    @patch('utils.get_opps.get_opp_request_details')
    def test_get_yesterdays_opps(self, m_get_opp_request_details, m_g_op,  m_yester):
        m_g_op.return_value = (mock_opps.mock_opps, 1)
        m_yester.return_value = (mock_opps.mock_opps, False)
        m_get_opp_request_details.return_value = (self.beta_opp_uri, {}, {})
        
        result = get_yesterdays_opps(filter_naics = False)
        expected = mock_opps.mock_opps
        self.assertEqual(result, expected)
#
    #@patch('utils.get_opps.find_yesterdays_opps')
    #@patch('utils.get_opps.get_opps')
    #@patch('utils.get_opps.get_opp_request_details')
    #def test_get_opps_two_pages(self, m_get_opp_request_details, m_g_op,  m_yester):            
    #    m_get_opp_request_details.return_value = (self.beta_opp_uri, {}, {})
    #    
    #    def m_g_op_side_effects(*args):
    #        if args[1] == {}:
    #            return (mock_opps.mock_opps, 1)
    #        elif args[1] == {'page': '1'}:
    #            return (mock_opps.mock_opps, 1)
    #        else:
    #            raise Exception
#
    #    def m_yester_side_effect(*args):
    #        if args[0] == mock_opps.mock_opps: 
    #            return (mock_opps.mock_opps, True)
    #        elif args[0] == mock_opps.mock_opp_one:
    #            return (mock_opps.mock_opp_one, False)
    #        else:
    #            raise Exception
    #    
    #    m_g_op.side_effect = m_g_op_side_effects
    #    m_yester.side_effect = m_yester_side_effect
    #    result = get_yesterdays_opps(filter_naics = False)
    #    expected = [mock_opps.mock_opp_one, mock_opps.mock_opp_one, 
    #                mock_opps.mock_opp_two, mock_opps.mock_opp_two]
    #    self.assertCountEqual(result, expected)
    
    @patch('utils.get_opps.get_doc_request_details')
    @patch('utils.get_opps.write_zip_content')
    @requests_mock.Mocker()
    def test_get_docs(self, m_write_zip_content, m_get_doc_request_details, mock_request):
        opp_id = '123'
        url = f'https://api.sam.gov/prod/opportunity/v1/api/{opp_id}/resources/download/zip'
        m_get_doc_request_details.return_value = url
        m_write_zip_content.return_value = ['test.pdf']
        mock_request.register_uri('GET',
                                  url = url,
                                  status_code = 200)
        result = get_docs('123', self.out_path)
        expected = ['test.pdf']
        self.assertEqual(result, expected)

    @patch('utils.get_opps.get_doc_text')
    def test_get_attachment_data(self, mock_get_doc_text):
        mock_get_doc_text.return_value = 'test'
        url = 'test'
        result = get_attachment_data('test.txt', url)
        expected = mock_opps.mock_attachment_data
        self.assertEqual(result, expected)
    
    @patch('utils.get_opps.get_attachment_data')
    @patch('utils.get_opps.get_doc_text')    
    @patch('utils.get_opps.get_docs')
    @patch('utils.get_opps.schematize_opp')
    def test_transform_opps(self, m_schematize_opp, m_g_docs, m_g_doc_text, m_g_attachment_data):
        m_schematize_opp.return_value = self.mock_schematized_opp_one
        m_g_docs.return_value = ['test.pdf']
        m_g_doc_text.return_value = 'test'
        m_g_attachment_data.return_value = mock_opps.mock_attachment_data
        result = transform_opps([mock_opps.mock_opp_one], self.out_path)
        # repeat 3 times since opps has three records
        expected = [mock_opps.mock_transformed_opp_one]
        self.assertEqual(result, expected)

    # def test_schematize_opp(self):
    #     so = schematize_opp(mock_opp_one)
    #     self.assertEqual(so['notice type'], 'opportunity')


if __name__ == '__main__':
    unittest.main()