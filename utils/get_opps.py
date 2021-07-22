import logging
import os
import sys
import re
import datetime
import urllib3
import shutil
import hashlib
import urllib

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.get_doc_text import get_doc_text
from utils.sam_utils import get_org_info, write_zip_content, get_notice_data, schematize_opp, \
    naics_filter, find_yesterdays_opps, sol_type_filter
from utils.request_utils import requests_retry_session, get_opps, get_opp_request_details, \
    get_doc_request_details

logger = logging.getLogger(__name__)

def get_opportunities_search_url(api_key=None, page_size=500, postedFrom=None, postedTo=None, target_sol_types="o,k"):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_string = datetime.datetime.strftime(yesterday, '%m/%d/%Y')
    base_uri = os.getenv('SAM_API_URI') or "https://api.sam.gov/opportunities/v2/search"
    params = (
        ("api_key", os.getenv('SAM_API_KEY')),
        ("limit", page_size),
        ("postedFrom", postedFrom or yesterday_string),
        ("postedTo", postedTo or yesterday_string),
        ("ptype", target_sol_types)
    )
    get_string = "&".join([ "{}={}".format(item[0], item[1]) for item in params  ])
    return "{}?{}".format(base_uri, get_string)

def get_yesterdays_opps(filter_naics = True, limit = None, target_sol_types="o,k"):
    api_key = os.getenv('SAM_API_KEY')
    if not api_key:
        logger.error("No API key set. Please set the SAM_API_KEY environemnt variable.")
        logger.critical("No API key - Exiting .")
        exit(1)

    uri = get_opportunities_search_url(api_key=os.getenv('SAM_API_KEY'), target_sol_types=target_sol_types)
    logger.debug("Fetching yesterday's opps from {}".format(uri))

    totalRecords = 9999999
    offset = 0
    opps = []

    session = requests_retry_session()
    while offset < totalRecords and (not limit or len(opps) < limit):
        uri_with_offset = f'{uri}&offset={offset}'
        r = session.get(uri_with_offset, timeout = 100)
        data = r.json()
        totalRecords = data['totalRecords']
        offset += len(data['opportunitiesData'])

        opportunities_data = data['opportunitiesData']
        if filter_naics:
             opportunities_data = naics_filter(opportunities_data)
        opps.extend(opportunities_data)

    session.close()

    if limit and len(opps) > limit:
        opps = opps[:limit]

    return opps



def get_docs(opp, out_path):
    filelist = []
    http = urllib3.PoolManager()
    for file_url in (opp['resourceLinks'] or []):
        filename = os.path.join(out_path, hashlib.sha1(file_url.encode('utf-8')).hexdigest())
        with open(filename, 'wb') as out:
            r = http.request('GET', file_url, preload_content=False)
            shutil.copyfileobj(r,out)
            if 'Content-Disposition' in r.headers:
                content_disposition = r.headers['Content-Disposition'] # should be in the form "attachment; filename=Attachment+5+Non-Disclosure+Agreement.docx"
                match = re.search('filename=(.*)',content_disposition)
                if match and len(match.groups()) > 0:
                    real_filename = urllib.parse.unquote(match.group(1)).replace("+", " ")  # have to replace + with space because parse doesn't do that
                    real_filename_with_path = os.path.join(out_path, real_filename)
                    os.rename(filename, real_filename_with_path)
                    logger.info("Downloaded file {}".format(real_filename_with_path))
                    filelist.append( (real_filename_with_path, file_url) )
    http.clear()
    return filelist

def get_attachment_data(file_name, url):
    text = get_doc_text(file_name)
    fn = os.path.basename(file_name)
    machine_readable = True if text else False
    attachment_data = {'text': text, 
                       'url': url, 
                       'prediction': None, 
                       'decision_boundary': None, 
                       'validation': None, 
                       'trained': False,
                       'machine_readable': machine_readable,
                       'filename':fn}
    
    return attachment_data

def transform_opps(opps, out_path, skip_attachments=False):
    """Transform the opportunity data to fit the SRT's schema
    
    Arguments:
        opps {dict} -- a dictionary containing the JSON response of get_opps()
    """
    transformed_opps = []
    for opp in opps:
        schematized_opp = schematize_opp(opp)
        if not schematized_opp:
            continue
        if not skip_attachments:
            file_list = get_docs(schematized_opp, out_path=out_path)
            if file_list:
                attachment_data = [ get_attachment_data(file_and_url_tuple[0], file_and_url_tuple[1]) for file_and_url_tuple in file_list ]
                schematized_opp['attachments'].extend(attachment_data)
        transformed_opps.append(schematized_opp)
    return transformed_opps

def main(limit=None, filter_naics = True, target_sol_types=("k","o"), skip_attachments=False):
    try:
        out_path = os.path.join(os.getcwd(), 'attachments')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        # opps = get_yesterdays_opps(limit=limit, filter_naics=filter_naics, target_sol_types=target_sol_types)
        opps = get_yesterdays_opps(limit=limit, filter_naics=filter_naics, target_sol_types=target_sol_types)
        if not opps:
            return []
        transformed_opps = transform_opps(opps, out_path, skip_attachments=skip_attachments)

    except Exception as e:
        logger.critical(f"Exception {e} getting solicitations", exc_info=True)
        sys.exit(1)

    return transformed_opps

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    transformed_opps = main()
    