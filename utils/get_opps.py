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
from utils.sam_utils import schematize_opp
from utils.request_utils import requests_retry_session

logger = logging.getLogger(__name__)

def get_opportunities_search_url(api_key=None, page_size=500, postedFrom=None, postedTo=None, target_sol_types="o,k", from_date="yesterday", to_date="yesterday"):
    '''

    Args:
        api_key:
        page_size:
        postedFrom: formatted mm/dd/yyyy or the default string "yesterday" if you want the function to use yesterday
        postedTo:  formatted mm/dd/yyyy or the default string "yesterday" if you want the function to use yesterday
        target_sol_types:
        from_date:
        to_date:

    Returns:

    '''
    if from_date=="yesterday":
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        from_date = datetime.datetime.strftime(yesterday, '%m/%d/%Y')
    else:
        from_date = sam_format_date(from_date)

    if to_date=="yesterday":
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        to_date = datetime.datetime.strftime(yesterday, '%m/%d/%Y')
    else:
        to_date = sam_format_date(to_date)

    base_uri = os.getenv('SAM_API_URI') or "https://api.sam.gov/opportunities/v2/search"
    params = (
        ("api_key", os.getenv('SAM_API_KEY')),
        ("limit", page_size),
        ("postedFrom", postedFrom or from_date),
        ("postedTo", postedTo or to_date),
        ("ptype", target_sol_types)
    )
    get_string = "&".join([ "{}={}".format(item[0], item[1]) for item in params  ])
    return "{}?{}".format(base_uri, get_string)

def get_opp_from_sam(solNum):
    base_uri = os.getenv('SAM_API_URI') or "https://api.sam.gov/opportunities/v2/search"
    uri = base_uri + f"?solnum={solNum}&api_key={os.getenv('SAM_API_KEY')}&limit=1"
    session = requests_retry_session()
    r = session.get(uri, timeout = 100)
    data = r.json()
    if data['totalRecords'] == 0:
        return None
    session.close()
    return data['opportunitiesData'][0]

def sam_format_date(input_date):
    '''
    Try to format a date as mm/dd/yyyy.  It isn't too smart tho.
    Only works for dates in mm-dd-yyyy, a datetime, or a string already formatted as mm/dd/yyyy
    Args:
        input_date: date in various formats. Will do our best to fix it

    Returns: string with date in format mm/dd/yyyy

    '''

    if isinstance(input_date, datetime.date):
        return input_date.strftime("%m/%d/%Y")

    parts = input_date.split("-")
    if len(parts) > 2:
        # assume mm-dd-yyyy
        return parts[0]+"/"+parts[1]+"/"+parts[2]

    # for now assume we got it in the right format
    return input_date

def get_opps_for_day(opportunity_filter_function = None, limit = None, target_sol_types="o,k", from_date="yesterday", to_date="yesterday", filter=None):
    '''

    Args:
        opportunity_filter_function: function that returns true for opportunites we want to process
        limit: Number of opportunities to pull
        target_sol_types: Use the sam.gov API type codes. Defaults to Solicitiation and Combined Sol/Synopsys
        from_date: formatted mm/dd/yyyy or the default string "yesterday" if you want the function to use yesterday
        to_date: formatted mm/dd/yyyy or the default string "yesterday" if you want the function to use yesterday
        filter: Additional query string arguments for the SAM.gov api call

    Returns:

    '''
    api_key = os.getenv('SAM_API_KEY')
    if not api_key:
        logger.error("No API key set. Please set the SAM_API_KEY environemnt variable.")
        logger.critical("No API key - Exiting .")
        exit(1)

    uri = get_opportunities_search_url(api_key=os.getenv('SAM_API_KEY'), target_sol_types=target_sol_types,from_date=from_date, to_date=to_date)
    if filter:
        uri += "&" + filter
    logger.debug("Fetching yesterday's opps from {}".format(uri))

    totalRecords = 9999999
    final_opp_data = []
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

        for o in opportunities_data:
            logger.debug(o['postedDate'] + " " + o['solicitationNumber'] + " " + o['title'] + ' ' + o['active'])

        if opportunity_filter_function:
            opportunities_data = [o for o in opportunities_data if opportunity_filter_function(o) ]

        opps.extend(opportunities_data)

        logger.info(f"{len(opportunities_data)} opportunities matched the filter out of {len(data['opportunitiesData'])} total opps in this round")

    session.close()

    if limit and len(opps) > limit:
        opps = opps[:limit]

    return opps


def make_attachement_request(file_url, http):
    r = None
    try:
        r = http.request('GET', file_url, preload_content=False)
    except Exception as e:
        logger.error(f"{type(e)} encountered when trying to download an attachement from {file_url}")
        # some URLs are malformed and use beta.sam.gov when they should be sam.gov, so try that
        if re.search('beta.sam.gov', file_url):
            new_file_url = file_url.replace('beta.sam.gov', 'sam.gov')
            logger.info(f"rewriting attachment url from {file_url} to {new_file_url} ")
            try:
                r = http.request('GET', new_file_url, preload_content=False)
                shutil.copyfileobj(r, out)
            except Exception as e2:
                logger.error(f"{type(e)} encountered when trying to download fixed attachment URL {file_url}")
    return r


def get_docs(opp, out_path):
    filelist = []
    http = urllib3.PoolManager()
    for file_url in (opp['resourceLinks'] or []):
        filename = os.path.join(out_path, hashlib.sha1(file_url.encode('utf-8')).hexdigest())
        with open(filename, 'wb') as out:
            r = make_attachement_request(file_url, http)
            if r and 'Content-Disposition' in r.headers:
                shutil.copyfileobj(r, out)
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

def main(limit=None, opportunity_filter_function=None, target_sol_types=("k","o"), skip_attachments=False, from_date="yesterday", to_date="yesterday"):
    '''

    Args:
        limit:
        opportunity_filter_function: A function that returns true if we are interested in the opportuntiy
        target_sol_types:
        skip_attachments: Will skip downloading attachments if true. Default to false.
        from_date: formatted mm/dd/yyyy or the default string "yesterday" if you want the function to use yesterday
        to_date: formatted mm/dd/yyyy or the default string "yesterday" if you want the function to use yesterday

    Returns:

    '''
    try:
        out_path = os.path.join(os.getcwd(), 'attachments')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        # opps = get_yesterdays_opps(limit=limit, filter_naics=filter_naics, target_sol_types=target_sol_types)
        opps = get_opps_for_day(limit=limit, opportunity_filter_function=opportunity_filter_function, target_sol_types=target_sol_types, from_date=from_date, to_date=to_date)
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
    