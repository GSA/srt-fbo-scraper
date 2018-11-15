import unittest
import os
from utils.fbo_nightly_scraper import NightlyFBONotices
from fixtures import nightly_file, json_str, filtered_json_str, nightly_data
from utils.get_fbo_attachments import FboAttachments
import requests
import httpretty

def exceptionCallback(request, uri, headers):
    '''
    Create a callback body that raises an exception when opened. This simulates a bad request.
    '''
    raise requests.ConnectionError('Raising a connection error for the test. You can ignore this!')

temp_outfile_path = 'temp_test_file'
fake_fbo_url = 'https://www.fbo.gov/fake.php'

class NightlyFBONoticesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        notice_types= ['MOD','PRESOL','COMBINE', 'AMDCSS']
        naics = ['334111', '334118', '3343', '33451', '334516', '334614', '5112',
                 '518', '54169', '54121', '5415', '54169', '61142']
        cls.nfbo = NightlyFBONotices(date=20180506, notice_types=notice_types, naics=naics)
        cls.file_lines = nightly_file.nightly_file

    @classmethod
    def tearDownClass(cls):
        cls.nfbo = None
        cls.file_lines = None
        cls.empty_file_lines = None

    def test__id_and_count_notice_tags(self):
        result = NightlyFBONoticesTestCase.nfbo._id_and_count_notice_tags(NightlyFBONoticesTestCase.file_lines)
        expected = {'PRESOL': 1, 'COMBINE': 1, 'ARCHIVE': 1, 
                    'AWARD': 1, 'MOD': 1, 'AMDCSS': 1, 'SRCSGT': 1, 'UNARCHIVE': 1}
        self.assertDictEqual(result, expected)

    def test__merge_dicts(self):
        notice = [{'a': '123'}, {'b': '345'}, {'c': '678'}, {'c': '9'}]
        result = NightlyFBONoticesTestCase.nfbo._merge_dicts(notice)
        expected = {'a': '123', 'b': '345', 'c': '678 9'}
        self.assertDictEqual(result, expected)

    def test_pseudo_xml_to_json(self):
        result = "".join(sorted(NightlyFBONoticesTestCase.nfbo.pseudo_xml_to_json(NightlyFBONoticesTestCase.file_lines)))
        expected = "".join(sorted(json_str.json_str))
        self.assertEqual(result, expected)

    def test_filter_json(self):
        result = "".join(sorted(NightlyFBONoticesTestCase.nfbo.filter_json(json_str.json_str)))
        expected = "".join(sorted(filtered_json_str.filtered_json_str))
        self.assertEqual(result, expected)
    

class FboAttachmentsTestCase(unittest.TestCase):
    
    def setUp(self):
        self.fboa = FboAttachments(nightly_data = nightly_data.nightly_data)

    def tearDown(self):
        self.fboa = None
        if os.path.exists(temp_outfile_path):  
            os.remove(temp_outfile_path)
    
    def test_get_divs(self):
        body_with_div = u'''
                            <div class="notice_attachment_ro notice_attachment_last">
                            <div>	
                        <div class="file"><input type="hidden" name="dnf_class_values[procurement_notice_archive][packages][5][files][0][file][0][preview]" value="&lt;a href='/utils/view?id=d95550fb782f53357ed65db571ef9186' target='_blank' title='Download/View FA852618Q0033_______0001.pdf' class='file'&gt;FA852618Q0033_______0001.pdf&lt;/a&gt;"><a href='/utils/view?id=d95550fb782f53357ed65db571ef9186' target='_blank' title='Download/View FA852618Q0033_______0001.pdf' class='file'>FA852618Q0033_______0001.pdf</a> (16.54 Kb)</div>
                        </div>
                            <div><span class="label">Description:</span> Amendment 0001</div>	</div>


                            </div><!-- widget -->
                        
                            </div>
        '''
        httpretty.register_uri(httpretty.GET, uri=fake_fbo_url, body=body_with_div)
        result = self.fboa.get_divs(fake_fbo_url)
        expected = []
        self.assertEqual(len(result), len(expected))
    
    @httpretty.activate
    def test_get_divs_wrong_url(self):
        httpretty.register_uri(httpretty.GET, uri=fake_fbo_url, body='No divs in here')
        result = self.fboa.get_divs(fake_fbo_url)
        expected = []
        self.assertEqual(len(result), len(expected))
    
    @httpretty.activate
    def test_get_divs_non200_url(self):
        httpretty.register_uri(httpretty.GET, uri=fake_fbo_url, status=404)
        result = self.fboa.get_divs(fake_fbo_url)
        expected = []
        self.assertEqual(len(result), len(expected))
        
    @httpretty.activate
    def test_get_divs_connection_error(self):
        httpretty.register_uri(method=httpretty.GET, uri=fake_fbo_url, status=200, body=exceptionCallback)
        result = self.fboa.get_divs(fake_fbo_url)
        expected = []
        self.assertEqual(len(result), len(expected))
            
    def test_insert_attachments(self):
        text = "This is a test"
        notice = {'a': '1', 'b': '2'}
        with open(temp_outfile_path, 'w') as f:
            f.write(text)
        file_list = [(temp_outfile_path,fake_fbo_url)]
        result = self.fboa.insert_attachments(file_list, notice)
        expected = {'a': '1',
                    'b': '2',
                    'attachments':[{'text':text, 
                                    'url':fake_fbo_url,
                                    'prediction':None, 
                                    'decision_boundary':None,
                                    'validation':None,
                                    'trained':False}]
        }
        self.assertDictEqual(result, expected)

    @httpretty.activate
    def test_size_check(self):
        httpretty.register_uri(httpretty.HEAD, uri=fake_fbo_url, body='This is less than 500MB')
        result = self.fboa.size_check(fake_fbo_url)
        expected = True
        self.assertEqual(result, expected)

    @httpretty.activate
    def test_size_check_non200_url(self):
        httpretty.register_uri(httpretty.HEAD, uri=fake_fbo_url, status=404)
        result = self.fboa.size_check(fake_fbo_url)
        expected = False
        self.assertEqual(result, expected)

    @httpretty.activate
    def test_size_check_connection_error(self):
        httpretty.register_uri(method=httpretty.HEAD, uri=fake_fbo_url, status=200, body=exceptionCallback)
        result = self.fboa.size_check(fake_fbo_url)
        expected = False
        self.assertEqual(result, expected)
    
    def test_get_filename_from_cd(self):
        content_disposition = 'attachment; filename="test.doc"'
        result = self.fboa.get_filename_from_cd(content_disposition)
        expected = 'test.doc'
        self.assertEqual(result, expected)

    def test_get_filename_from_bad_cd(self):
        content_disposition = 'no file name in here!'
        result = self.fboa.get_filename_from_cd(content_disposition)
        expected = None
        self.assertEqual(result, expected)
    
    def test_get_file_name(self):
        pass
    
    def test_write_attachments(self):
        pass

    def test_update_nightly_data(self):
        pass

        
if __name__ == '__main__':
    unittest.main()