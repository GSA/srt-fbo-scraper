import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import requests
import json
import responses
import requests_mock
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from utils.fbo_nightly_scraper import clean_line_text, get_email_from_url, extract_emails, \
    get_redirect_url, handle_archive_redirect, get_notice_url_from_archive_list, handle_dla_url, \
    merge_dicts, id_and_count_notice_tags, pseudo_xml_to_json, filter_json, get_nightly_data
from fixtures.nightly_file import nightly_file
from fixtures import handle_archive_redirect_table, get_notice_url_from_archive_list_table, \
    pseudo_xml_to_json_expected, filter_json_expected, get_nightly_data_expected


class FboNightlyScraperTestCase(unittest.TestCase):
    '''
    Test cases for functions in fbo_nightly_scraper.py
    '''
    
    def setUp(self):
        self.notice_types= ['MOD','PRESOL','COMBINE', 'AMDCSS']
        self.naics = ['334111', '334118', '3343', '33451', '334516', '334614', '5112',
                 '518', '54169', '54121', '5415', '54169', '61142']
        self.file_lines = nightly_file
        self.maxDiff = None

    def tearDown(self):
        self.notice_types = None
        self.naics = None
        self.file_lines = None

    def test_clean_line_text_garbage(self):
        '''
        See that it strips out garbage
        '''
        result = clean_line_text('&nbsp;\n')
        expected = ''
        self.assertEqual(result, expected)

    def test_clean_line_text_some_garbage(self):
        '''
        See that it strips out garbage
        '''
        text_to_clean = '<p style="MARGIN-BOTTOM: 0pt; LINE-HEIGHT: normal"><a name="OLE_LINK2"></a><a name="OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">SOLICITATION FOR NSN:</span> </span></a><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">2915009189013, 0076482892, GUIDE, SPRING, ONTIC (45934) P/N: 557568, FOB ORIGIN, INSPECTION/ACCEPTANCE AT DESTINATION. <span style="mso-spacerun: yes">&nbsp;</span>ONTIC IS THE ONLY APPROVED SOURCES FOR THIS ITEM.<span style="mso-spacerun: yes">&nbsp; </span>DLA DOES NOT CURRENTLY HAVE AN APPROVED TECHNICAL DATA PACKAGE AVAILABLE FOR THIS NSN.<span style="mso-spacerun: yes">&nbsp; </span>ANY MANUFACTURER, OTHER THAN THE APPROVED SOURCE, WISHING TO SUBMIT A PROPOSAL ON THIS ITEM MUST SUBMIT A COMPLETE SOURCE APPROVAL REQUEST (SAR) PACKAGE.<span style="mso-spacerun: yes">&nbsp; </span>SOLICITATION WILL BE FOR A FIRM FIXED PRICE QUANTITY OF 418 EACH.<span style="mso-spacerun: yes">&nbsp; </span>SOLICITATION WILL PUBLISH ON OR ABOUT DECEMBER 12, 2018 WITH A CLOSING DATE OF JANUARY 11, 2019.<span style="mso-spacerun: yes">&nbsp; </span>DELIVERY REQUESTED WILL BE 365 DAYS ARO.<span style="mso-spacerun: yes">&nbsp;&nbsp; </span>SAMPLING FOR INSPECTION &amp; TESTING SHALL BE IAW ANSI/ASQ Z1.4-2003. <span style="mso-spacerun: yes">&nbsp;</span>PPIRS APPLIES.<span style="mso-spacerun: yes">&nbsp; </span>THE FINAL CONTRACT AWARD DECISION MAY BE BASED UPON A COMBINATION OF PRICE, PAST PERFORMANCE, AND OTHER EVALUATION FACTORS AS DESCRIBED IN THE SOLICITATION.<span style="mso-spacerun: yes">&nbsp; </span>THE SOLICITATION WILL BE AVAILABLE VIA THE DLA-BSM INTERNET BID BOARD SYSTEM (DIBBS) AT </span></span></span><a href="https://www.dibbs.bsm.dla.mil"><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">https://www.dibbs.bsm.dla.mil</span></span></span></a><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: "> ON THE ISSUE DATE CITED IN THE RFP.<span style="mso-spacerun: yes">&nbsp; </span>FROM THE DIBBS HOMEPAGE, SELECT SOLICITATIONS, SELECT REQUEST FOR PROPOSAL (RFP)/INVITATION FOR BID (IFB) TAB, THEN SELECT SEARCH THE RFP/IFB DATABASE, THEN CHOOSE THE RFP YOU ARE SEARCHING FOR.<span style="mso-spacerun: yes">&nbsp; </span>RFP\'S ARE IN PORTABLE DOCUMENT FORMAT (PDF).<span style="mso-spacerun: yes">&nbsp; </span>TO DOWNLOAD AND VIEW THESE DOCUMENTS YOU WILL NEED THE LATEST VERSION OF ADOBE ACROBAT READER.<span style="mso-spacerun: yes">&nbsp; </span>THIS SOFTWARE IS AVAILABLE FREE AT </span></span></span><a href="http://www.adobe.com"><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">http://www.adobe.com</span></span></span></a><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">.<span style="mso-spacerun: yes">&nbsp; </span>A PAPER COPY OF THE SOLICIATION WILL NOT BE AVAILABLE TO REQUESTORS. EMAIL QUOTE TO DESIREE.MCCORMICK@DLA.MIL.</span></span></span></p>\n'
        result = clean_line_text(text_to_clean)
        expected = "https://www.dibbs.bsm.dla.mil SOLICITATION FOR NSN: 2915009189013, 0076482892, GUIDE, SPRING, ONTIC (45934) P/N: 557568, FOB ORIGIN, INSPECTION/ACCEPTANCE AT DESTINATION. ONTIC IS THE ONLY APPROVED SOURCES FOR THIS ITEM. DLA DOES NOT CURRENTLY HAVE AN APPROVED TECHNICAL DATA PACKAGE AVAILABLE FOR THIS NSN. ANY MANUFACTURER, OTHER THAN THE APPROVED SOURCE, WISHING TO SUBMIT A PROPOSAL ON THIS ITEM MUST SUBMIT A COMPLETE SOURCE APPROVAL REQUEST (SAR) PACKAGE. SOLICITATION WILL BE FOR A FIRM FIXED PRICE QUANTITY OF 418 EACH. SOLICITATION WILL PUBLISH ON OR ABOUT DECEMBER 12, 2018 WITH A CLOSING DATE OF JANUARY 11, 2019. DELIVERY REQUESTED WILL BE 365 DAYS ARO. SAMPLING FOR INSPECTION & TESTING SHALL BE IAW ANSI/ASQ Z1.4-2003. PPIRS APPLIES. THE FINAL CONTRACT AWARD DECISION MAY BE BASED UPON A COMBINATION OF PRICE, PAST PERFORMANCE, AND OTHER EVALUATION FACTORS AS DESCRIBED IN THE SOLICITATION. THE SOLICITATION WILL BE AVAILABLE VIA THE DLA-BSM INTERNET BID BOARD SYSTEM (DIBBS) AT https://www.dibbs.bsm.dla.mil ON THE ISSUE DATE CITED IN THE RFP. FROM THE DIBBS HOMEPAGE, SELECT SOLICITATIONS, SELECT REQUEST FOR PROPOSAL (RFP)/INVITATION FOR BID (IFB) TAB, THEN SELECT SEARCH THE RFP/IFB DATABASE, THEN CHOOSE THE RFP YOU ARE SEARCHING FOR. RFP'S ARE IN PORTABLE DOCUMENT FORMAT (PDF). TO DOWNLOAD AND VIEW THESE DOCUMENTS YOU WILL NEED THE LATEST VERSION OF ADOBE ACROBAT READER. THIS SOFTWARE IS AVAILABLE FREE AT http://www.adobe.com. A PAPER COPY OF THE SOLICIATION WILL NOT BE AVAILABLE TO REQUESTORS. EMAIL QUOTE TO DESIREE.MCCORMICK@DLA.MIL."
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_email_from_url(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                                  url = url ,
                                  text = '''<div><a href="mailto:foo.bar.bax.civ@mail.mil" onmousedown="_sendEvent('Outbound MailTo','foo.bar.bax.civ@mail.mil','',0);">foo.bar.bax.civ@mail.mil</a></div>''',
                                  status_code = 200)
        result = get_email_from_url(url)
        expected = ['mailto:foo.bar.bax.civ@mail.mil']
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_email_from_url_404(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                                  url = url,
                                  text = 'foo',
                                  status_code = 404)
        result = get_email_from_url(url)
        expected = []
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_email_from_url_exception(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                               url = url,
                               exc = requests.exceptions.ConnectionError)
        result = get_email_from_url(url)
        expected = None
        self.assertEqual(result, expected)

    def test_extract_emails_contact_w_email(self):
        notice = {'CONTACT':'foo.bar@gsa.gov'}
        result = extract_emails(notice)
        expected = ['foo.bar@gsa.gov']
        self.assertEqual(result, expected)

    def test_extract_emails_email_w_email(self):
        notice = {'CONTACT':'no email here :(',
                  'EMAIL':'foo.bar@gsa.gov'}
        result = extract_emails(notice)
        expected = ['foo.bar@gsa.gov']
        self.assertEqual(result, expected)

    def test_extract_emails_desc_w_email(self):
        notice = {'CONTACT':'no email here :(',
                  'DESC':'foo.bar@gsa.gov'}
        result = extract_emails(notice)
        expected = ['foo.bar@gsa.gov']
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_extract_emails_scrape_needed(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                                  url = url ,
                                  text = '''<div><a href="mailto:foo.bar.civ@mail.mil" onmousedown="_sendEvent('Outbound MailTo','foo.bar.bax.civ@mail.mil','',0);">foo.bar.bax.civ@mail.mil</a></div>''',
                                  status_code = 200)
        notice = {'CONTACT':'no email here :(',
                  'DESC':'and no email here',
                  'URL':url}
        result = extract_emails(notice)
        expected = ['foo.bar.civ@mail.mil']
        self.assertEqual(result, expected)

    def test_get_redirect_url(self):
        class HeadHeaders:
            def __init__(self):
                self.headers = {'Location': '/index?s=opportunity&mode=list&tab=archives'}
        h = HeadHeaders()
        result = get_redirect_url(h)
        expected = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        self.assertEqual(result, expected)

    @patch('utils.fbo_nightly_scraper.get_notice_url_from_archive_list')
    @requests_mock.Mocker()
    def test_handle_archive_redirect(self, mock_get_notice_url_from_archive_list, mock_request):
        mock_get_notice_url_from_archive_list.return_value = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=6577a9fff18f484f728af34bb6179872&tab=core&_cview=0'
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        jar = requests_mock.CookieJar()
        jar.set('foo', 'bar', domain='fbo.gov')
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = handle_archive_redirect_table.body,
                                  status_code = 200,
                                  cookies = jar,
                                  complete_qs = True)
        result = handle_archive_redirect('www.test.gov',
                                         redirect_url,
                                         {'foo': 'bar'},
                                         'notice_date',
                                         'notice_type')
        expected = mock_get_notice_url_from_archive_list.return_value
        self.assertEqual(result, expected)

    @patch('utils.fbo_nightly_scraper.get_notice_url_from_archive_list')
    @requests_mock.Mocker()
    def test_handle_archive_redirect_exception(self, mock_get_notice_url_from_archive_list, mock_request):
        mock_get_notice_url_from_archive_list.return_value = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=6577a9fff18f484f728af34bb6179872&tab=core&_cview=0'
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  exc = requests.exceptions.ConnectTimeout)
        result = handle_archive_redirect('www.test.gov',
                                         redirect_url,
                                         {'foo': 'bar'},
                                         'notice_date',
                                         'notice_type')
        expected = None
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_url_from_archive_list_combine_match(self, mock_request):
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        soup = BeautifulSoup(handle_archive_redirect_table.body, 'html.parser')    
        archive_list = soup.find('table', {'class':'list'}).find_all('tr')
        notice_date = '052218'
        notice_type = 'COMBINE'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = handle_archive_redirect_table.body,
                                  status_code = 200)
        result = get_notice_url_from_archive_list(redirect_url, 
                                                  archive_list, 
                                                  notice_date, 
                                                  notice_type)
        expected = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=6577a9fff18f484f728af34bb6179872&tab=core&_cview=0'
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_url_from_archive_list_combine_combine_mod_match(self, mock_request):
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        soup = BeautifulSoup(get_notice_url_from_archive_list_table.body, 'html.parser')    
        archive_list = soup.find('table', {'class':'list'}).find_all('tr')
        notice_date = '092718'
        notice_type = 'COMBINE'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = get_notice_url_from_archive_list_table.body,
                                  status_code = 200)
        result = get_notice_url_from_archive_list(redirect_url, 
                                                  archive_list, 
                                                  notice_date, 
                                                  notice_type)
        expected = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=0aaaf3e46120ab174c4710d6a3592c9f&tab=core&_cview=1'
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_url_from_archive_list_combine_mod_match(self, mock_request):
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        soup = BeautifulSoup(get_notice_url_from_archive_list_table.body, 'html.parser')    
        archive_list = soup.find('table', {'class':'list'}).find_all('tr')
        notice_date = '092018'
        notice_type = 'MOD'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = get_notice_url_from_archive_list_table.body,
                                  status_code = 200)
        result = get_notice_url_from_archive_list(redirect_url, 
                                                  archive_list, 
                                                  notice_date, 
                                                  notice_type)
        expected = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=a97a12ba6c20259ec5fefd436123b0d1&tab=core&_cview=1'
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_url_from_archive_list_amdcss_match(self, mock_request):
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        soup = BeautifulSoup(get_notice_url_from_archive_list_table.body, 'html.parser')    
        archive_list = soup.find('table', {'class':'list'}).find_all('tr')
        notice_date = '091818'
        notice_type = 'AMDCSS'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = get_notice_url_from_archive_list_table.body,
                                  status_code = 200)
        result = get_notice_url_from_archive_list(redirect_url, 
                                                  archive_list, 
                                                  notice_date, 
                                                  notice_type)
        expected = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=84701bd4a3fb4ee5638f62fcd8c675e9&tab=core&_cview=1'
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_url_from_archive_list_presol_match(self, mock_request):
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        soup = BeautifulSoup(get_notice_url_from_archive_list_table.body, 'html.parser')    
        archive_list = soup.find('table', {'class':'list'}).find_all('tr')
        notice_date = '011719'
        notice_type = 'PRESOL'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = get_notice_url_from_archive_list_table.body,
                                  status_code = 200)
        result = get_notice_url_from_archive_list(redirect_url, 
                                                  archive_list, 
                                                  notice_date, 
                                                  notice_type)
        expected = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=1482b1265345e7a345e539789e68ea65&tab=core&_cview=1'
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_notice_url_from_archive_list_no_match(self, mock_request):
        redirect_url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=archives'
        soup = BeautifulSoup(get_notice_url_from_archive_list_table.body, 'html.parser')    
        archive_list = soup.find('table', {'class':'list'}).find_all('tr')
        notice_date = '011715'
        notice_type = 'PRESOL'
        mock_request.register_uri('GET',
                                  url = redirect_url,
                                  content = get_notice_url_from_archive_list_table.body,
                                  status_code = 200)
        result = get_notice_url_from_archive_list(redirect_url, 
                                                  archive_list, 
                                                  notice_date, 
                                                  notice_type)
        expected = None
        self.assertEqual(result, expected)

    @patch('utils.fbo_nightly_scraper.get_redirect_url')
    @requests_mock.Mocker()
    def test_handle_dla_url(self, mock_get_redirect_url, mock_request):
        mock_get_redirect_url.return_value = 'https://www.testredirect.gov'
        url = 'https://www.test.gov/spg/dla'
        notice_date = '011715'
        notice_type = 'PRESOL'
        mock_request.register_uri('HEAD',
                                  url = url,
                                  text = 'test',
                                  headers = {'Location':mock_get_redirect_url.return_value},
                                  status_code = 302)
        result = handle_dla_url(url, notice_date, notice_type)
        expected = mock_get_redirect_url.return_value
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_handle_dla_url_exception(self, mock_request):
        url = 'https://www.test.gov/spg/dla'
        notice_date = '011715'
        notice_type = 'PRESOL'
        mock_request.register_uri('HEAD',
                                  url = url,
                                  exc = requests.exceptions.ConnectionError)
        result = handle_dla_url(url, notice_date, notice_type)
        expected = None
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_handle_dla_url_404(self, mock_request):
        url = 'https://www.test.gov/spg/dla'
        notice_date = '011715'
        notice_type = 'PRESOL'
        mock_request.register_uri('HEAD',
                                  url = url,
                                  text = 'test',
                                  status_code = 404)
        result = handle_dla_url(url, notice_date, notice_type)
        expected = None
        self.assertEqual(result, expected)

    @patch('utils.fbo_nightly_scraper.handle_archive_redirect')
    @patch('utils.fbo_nightly_scraper.get_redirect_url')
    @requests_mock.Mocker()
    def test_handle_dla_url_archive(self, 
                                    mock_handle_archive_redirect, 
                                    mock_get_redirect_url, 
                                    mock_request):
        mock_handle_archive_redirect.return_value = 'https://www.foo.gov'
        mock_get_redirect_url.return_value = 'https://www.testredirect.gov/archive'
        url = 'https://www.test.gov/spg/dla'
        notice_date = '011715'
        notice_type = 'PRESOL'
        jar = requests_mock.CookieJar()
        jar.set('foo', 'bar', domain='fbo.gov')
        mock_request.register_uri('HEAD',
                                  url = url,
                                  text = 'test',
                                  headers = {'Location':mock_get_redirect_url.return_value},
                                  status_code = 302,
                                  cookies = jar)
        result = handle_dla_url(url, notice_date, notice_type)
        expected = mock_handle_archive_redirect.return_value
        self.assertEqual(result, expected)

    @patch('utils.fbo_nightly_scraper.handle_archive_redirect')
    @patch('utils.fbo_nightly_scraper.get_redirect_url')
    @requests_mock.Mocker()
    def test_handle_dla_url_list(self, 
                                 mock_handle_archive_redirect, 
                                 mock_get_redirect_url, 
                                 mock_request):
        mock_handle_archive_redirect.return_value = 'https://www.foo.gov'
        mock_get_redirect_url.return_value = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=list'
        url = 'https://www.test.gov/spg/dla'
        notice_date = '011715'
        notice_type = 'PRESOL'
        jar = requests_mock.CookieJar()
        jar.set('foo', 'bar', domain='fbo.gov')
        mock_request.register_uri('HEAD',
                                  url = url,
                                  text = 'test',
                                  headers = {'Location':mock_get_redirect_url.return_value},
                                  status_code = 302,
                                  cookies = jar)
        result = handle_dla_url(url, notice_date, notice_type)
        expected = mock_handle_archive_redirect.return_value
        self.assertEqual(result, expected)

    def test_handle_dla_url_non_dla_url(self):
        url = 'https://www.test.gov'
        notice_date = '011715'
        notice_type = 'PRESOL'
        result = handle_dla_url(url, notice_date, notice_type)
        expected = url
        self.assertEqual(result, expected)

    def test_id_and_count_notice_tags(self):
        result = id_and_count_notice_tags(self.file_lines)
        expected = {'PRESOL': 1, 'COMBINE': 1, 'ARCHIVE': 1,
                    'AWARD': 1, 'MOD': 1, 'AMDCSS': 1, 'SRCSGT': 1, 'UNARCHIVE': 1}
        self.assertEqual(result, expected)

    def test_merge_dicts(self):
        notice = [{'a': '123'}, {'b': '345'}, {'c': '678'}, {'c': '9'}]
        result = merge_dicts(notice)
        expected = {'a': '123', 'b': '345', 'c': '678 9'}
        self.assertEqual(result, expected)
    
    def test_pseudo_xml_to_json(self):
        result = pseudo_xml_to_json(self.file_lines)
        expected = pseudo_xml_to_json_expected.merge_notices_dict
        self.assertEqual(result, expected)
    
    def test_filter_json(self):
        notice_types = self.notice_types
        naics = self.naics
        merge_notices_dict = {'FAIROPP': [],
                              'PRESOL': [{'DATE': '0302',
                                'YEAR': '18',
                                'AGENCY': 'Department of the Air Force',
                                'OFFICE': 'Air Force Materiel Command',
                                'LOCATION': 'PK/PZ - Robins AFB',
                                'ZIP': '31098-1611',
                                'CLASSCOD': '39',
                                'NAICS': '334111',
                                'OFFADD': '215 Page Rd Robins AFB GA 31098-1611',
                                'SUBJECT': 'Sling, Multiple Leg  (Universal)',
                                'SOLNBR': 'FA8526-18-Q-0033',
                                'RESPDATE': '041818',
                                'CONTACT': 'Johnene P. McConnell, Contract Specialist, Phone 4782220039, Email johnene.mcconnell@us.af.mil - Alexander H Comportie, PCO, Phone 478-222-2672, Email alexander.comportie@us.af.mil',
                                'DESC': "This requirement is for a firm-fixed price contract with three one-year options for a Sling, Multiple Leg - (Universal), NSN: 3940-01-251-5979, Part Number 17G110012-1. This item is used to pick up handle, and install the crew entry door, the paratrooper doors, and various otherLRU's for the C-17 aircraft. The basic requirement is for a quantity of 8 each (includes first article), Test Plan (1 LO), and Test Report (1 LO). The three one-year Options are based on a quantity of 2 each. This requirement will be set-aside for Small Business. Offerors shall prepare their proposals in accordance with mandatory, explicit and detailed instructions contained in the RFQ. All responsible Small Business sources may submit a proposal to be considered by the contracting agency. TheGovernment will utilize the Past Performance Information Retrieval System (PPIRS), Excluded Parties List System (EPLS), and other Government databases to determine contractor status before evaluating proposals. Proposal will be evaluated based on criteria stated in the RFQ. We anticipate release of the RFQ on or around 19 March 2018 with an estimated response date of 18 April 2018. The RFQ and all attachments will be posted to the Federal Business Opportunities webpage (http://www.fbo.gov/). If you have questions or concerns related to this acquisition, contact the Contracting Specialist at email johnene.mcconnell@us.af.mil; telephone 478-222-0039. All data for this weapon system is considered EXPORT CONTROLLED.  Link ToDocument",
                                'URL': 'https://www.fbo.gov/spg/USAF/AFMC/WRALC/FA8526-18-Q-0033/listing.html',
                                'SETASIDE': 'Total Small Business  '}],
                              'SSALE': [],
                              'JA': [],
                              'EPSUPLOAD': [],
                              'FSTD': [],
                              'ITB': [],
                              'ARCHIVE': [{'DATE': '0215',
                                'YEAR': '18',
                                'AGENCY': 'Defense Logistics Agency',
                                'OFFICE': 'DLA Acquisition Locations',
                                'LOCATION': 'DLA Aviation - BSM',
                                'SOLNBR': 'SPE4A718T5652',
                                'NTYPE': 'AWARD',
                                'AWDNBR': 'SPE4A718P6190',
                                'ARCHDATE': '03022018  '}],
                              'AWARD': [{'DATE': '0302',
                                'YEAR': '18',
                                'AGENCY': 'Department of Agriculture',
                                'OFFICE': 'Agricultural Marketing Service',
                                'LOCATION': 'Commodity Procurement Staff',
                                'ZIP': '20250',
                                'CLASSCOD': '89',
                                'NAICS': '311211',
                                'OFFADD': '1400 Independence Ave., SW Washington, DC 20250 Washington DC 20250',
                                'SUBJECT': 'Bakery Flour Products for use in Domestic Food Assistance Programs',
                                'SOLNBR': '12-3J14-18-S-0171',
                                'NTYPE': 'PRESOL',
                                'CONTACT': 'Clyde King, Contract Specialist, Phone 816-926-2610, Fax 816-823-2303, Email CLYDE.KING@AMS.USDA.GOV - Jeffrey Jackson, Contracting Officer, Phone 816-926-2530, Fax 816-823-2303, Email Jeffrey.Jackson@ams.usda.gov',
                                'AWDNBR': '12-3J14-18-P-0800',
                                'AWDAMT': '$79,384.32',
                                'AWDDATE': '030118',
                                'AWARDEE': 'MENNEL MILLING COMPANY, INC, PO BOX 806, FOSTORIA, OH 44830-0806 US',
                                'DESC': 'PCA - 12-3J14-18-S-0171 - BAKERY FLOUR - 3/2/18.    ',
                                'URL': 'https://www.fbo.gov/notices/2170cab752876789ce7b53117d45e167'}],
                              'DELETE': [],
                              'MOD': [{'DATE': '0302',
                                'YEAR': '18',
                                'AGENCY': 'Department of Agriculture',
                                'OFFICE': 'Agricultural Research Service',
                                'LOCATION': 'Western Business Service Center',
                                'ZIP': 'N/A',
                                'CLASSCOD': 'Z',
                                'NAICS': '238160',
                                'OFFADD': '',
                                'SUBJECT': 'Remove and replace roof to riding barn',
                                'SOLNBR': '1232SD18Q0005',
                                'NTYPE': 'PRESOL',
                                'RESPDATE': '030918',
                                'CONTACT': 'Louise L. Snitz, Phone 510-559-6022, Fax 510-559-6023, Email louise.snitz@ars.usda.gov',
                                'DESC': 'The 2nd site visitAttendee Listand additional Q&As isposted. An edited SOW is posted withsome clarifications.  USDA, ARS, Grazinglands Research Laboratory, located at 7207 W. Cheyenne Street, El Reno, OK 73036 requires roof work on BD24 (Riding Hall) to include: 1-1. Remove existing roof panels 1-2. Remove and replace an estimated 500 LF 1" x 8" contractor provided decking 1-3. Replace with 250 sheets of 24\' x 3\' 26 gauge galvalume PBR panels, and 64 pieces formed R panels ridge caps 1-4. Install contractor provided 192 LF Rake Edge of comparable color 1-5. Discard old roof panels and old decking  ',
                                'URL': 'https://www.fbo.gov/notices/95e10018e18cb6221341409548d7e858',
                                'SETASIDE': 'Total Small Business',
                                'POPCOUNTRY': 'US',
                                'POPZIP': '73036',
                                'POPADDRESS': '7207 W. Cheyenne Street El Reno, OK  '}],
                              'UNARCHIVE': [{'DATE': '0125',
                                'YEAR': '18',
                                'AGENCY': 'Department of the Army',
                                'OFFICE': 'U.S. Army Medical Command',
                                'LOCATION': 'REGIONAL HEALTH CONTRACT OFF CENTRAL',
                                'SOLNBR': 'W81K00-18-T-0077',
                                'NTYPE': 'SNOTE',
                                'ARCHDATE': '03022018'}],
                              'SRCSGT': [{'DATE': '0302',
                                'YEAR': '18',
                                'AGENCY': 'Department of Veterans Affairs',
                                'OFFICE': 'Sioux Falls VAMROC',
                                'LOCATION': 'Department of Veterans Affairs Medical and Regional Office Center',
                                'ZIP': '57105',
                                'CLASSCOD': 'S',
                                'NAICS': '562910',
                                'OFFADD': 'Department of Veterans Affairs;NETWORK 23 CONTRACTING OFFICE;2501 W. 22nd St.;Sioux Falls SD 57105',
                                'SUBJECT': 'S--636-18-3-9067-0218 DES MOINES Haz Waste RMW PHARM CSDP',
                                'SOLNBR': '36C26318Q9148',
                                'RESPDATE': '031218',
                                'ARCHDATE': '05112018',
                                'CONTACT': 'Scott Morrison, Contract Officer email: scott.morrison2@va.gov  mailto:scott.morrison2@va.gov scott.morrison2@va.gov',
                                'DESC': 'The Veterans Affairs Central Iowa Health Care System (VACIHCS) @ 3600 30th street, Des Moines, IA 50310 and five CBOC s (Ft. Dodge CBOC has two addresses, but is oneCBOC. Each location will require services) as a need for collecting, hauling, treatment and disposal of Hazardous and Non-Hazardous Waste, including pharmaceutical, Controlled Substance Destruction Program (CSDP) and Regulated Medical Waste (RMW) (including Reusable needles, Bulk, Chemo Waste and Pathological Waste). Waste servicesconsists of physically collecting, treatment and disposal of each waste type on a regularly scheduled basis, to be mutually determined by provider of service and the VACIHCS. Contractor shall provide all lab pack services, emergency spill response services, all primary collection containers, reusable sharps containers, mounting bracketsand floor mounts, carts for interim storage for reusable sharps system. Contractor shall provide all labor, materials and operations for each waste type listed. SOW will be broken out into four sections to reflect these different service types. Section A: RMW Bulk to include Chemo and Pathological. Section B: RMW Reusable sharpsservices. Section C: Pharmaceutical Waste Services. Section D: Hazardous waste.  For further details related to the pending procurement, see the full statement of work within the Request for Information, 36C26318Q9148.   scott.morrison2@va.gov',
                                'URL': 'https://www.fbo.gov/spg/VA/SFaVAMC/VAMCCO80220/36C26318Q9148/listing.html',
                                'EMAIL': ' scott.morrison2@va.gov',
                                'SETASIDE': 'N/A',
                                'POPZIP': '50310  '}],
                              'SNOTE': [],
                              'AMDCSS': [{'DATE': '0302',
                                'YEAR': '18',
                                'AGENCY': 'Department of the Air Force',
                                'OFFICE': 'Air Combat Command',
                                'LOCATION': '99 CONS',
                                'ZIP': '89191-7063',
                                'CLASSCOD': '58',
                                'NAICS': '334220',
                                'OFFADD': '5865 Swaab Blvd Nellis AFB NV 89191-7063',
                                'SUBJECT': 'Security Camera Intallation',
                                'SOLNBR': 'FA4861-18-Q-A008',
                                'NTYPE': 'COMBINE',
                                'RESPDATE': '031918',
                                'CONTACT': 'Stephen M. Colton, Phone 702-652-9333, Email Stephen.Colton@us.af.mil',
                                'DESC': 'The purpose of this Amendment is to post Questions & Answers 2.  ',
                                'URL': 'https://www.fbo.gov/spg/USAF/ACC/99CONS/FA4861-18-Q-A008/listing.html',
                                'SETASIDE': 'Total Small Business',
                                'POPCOUNTRY': 'US',
                                'POPZIP': '89191',
                                'POPADDRESS': 'Nellis AFB Las Vegas, NV  '}],
                              'COMBINE': [{'DATE': '0302',
                                'YEAR': '18',
                                'AGENCY': 'Department of the Air Force',
                                'OFFICE': 'Air Education and Training Command',
                                'LOCATION': '502d Contracting Squadron',
                                'ZIP': '78236-5253',
                                'CLASSCOD': '42',
                                'NAICS': '339999',
                                'OFFADD': '1655 Selfridge AvenueJBSA Lackland TX 78236-5253',
                                'SUBJECT': 'Extrication Hybrid Gloves',
                                'SOLNBR': 'FA301618U0096',
                                'RESPDATE': '030918',
                                'CONTACT': 'Lauren Macias, Phone 210-671-6415, Email lauren.macias.1@us.af.mil',
                                'DESC': 'Please see following attachment for full details.  ',
                                'URL': 'https://www.fbo.gov/spg/USAF/AETC/LackAFBCS/FA301618U0096/listing.html',
                                'SETASIDE': 'Total Small Business',
                                'POPCOUNTRY': 'US',
                                'POPZIP': '78236',
                                'POPADDRESS': 'JBSA Lackland Lackland, TX  '}]}
        result = filter_json(merge_notices_dict, notice_types, naics)
        expected = filter_json_expected.nightly_data
        #convert to json strings and sort since you cannot predict list order nested within dict
        result = "".join(sorted(json.dumps(result)))
        expected = "".join(sorted(json.dumps(expected)))
        self.assertEqual(result, expected)

    def test_get_nightly_data(self):
        #use it on real data for an end-to-end test
        date = '20190203'
        result = get_nightly_data(date = date)
        expected = get_nightly_data_expected.nightly_data
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()