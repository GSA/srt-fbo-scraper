import logging
import os
import sys
import json
import wget

import requests

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.get_doc_text import get_doc_text
from utils.sam_utils import get_org_info, write_zip_content, get_notice_data, schematize_opp, \
    naics_filter, find_yesterdays_opps
from utils.request_utils import requests_retry_session, get_opps, get_opp_request_details, \
    get_doc_request_details

logger = logging.getLogger(__name__)


def get_yesterdays_opps(filter_naics = True):
    uri, params, headers = get_opp_request_details()
    opps, total_pages = get_opps(uri, params, headers)
    if not opps and not total_pages:
        # no opps or maybe a request error
        return
    # use yesterday's since today's might not be complete at time of running the script
    opps, is_more_opps = find_yesterdays_opps(opps)
    if not is_more_opps:
        # Our results included opps beyond today and yesterday. Since the results are 
        # sorted in descending order by modifiedDate, there's no need to make another request
        if filter_naics:
            filtered_opps = naics_filter(opps)
            return filtered_opps
        return opps

    # the sgs/v1/search API starts at page 0
    page = 0
    while page <= total_pages:
        params.update({'page': str(page)})
        _opps, _ = get_opps(uri, params, headers)
        _opps, _is_more_opps = find_yesterdays_opps(_opps)
        opps.extend(_opps)
        if not _is_more_opps:
            break
        page += 1
    
    if filter_naics:
        filtered_opps = naics_filter(opps)
        return filtered_opps
    
    return opps

def get_docs(opp_id, out_path):
    """Download a zip archive of an opportunity's documents
    
    Arguments:
        opp_id {str} -- an opportunity id 
    """
    # see https://open.gsa.gov/api/opportunities-api
    # /#download-all-attachments-as-zip-for-an-opportunity

    uri = get_doc_request_details(opp_id)
    try:
        with requests_retry_session() as session:
            r = session.get(uri, timeout = 200)
    except Exception as e:
        logger.error(f"Exception {e} getting opps from {uri}", exc_info=True)
        #sys.exit(1)
        logger.warning("Falling back to wget for {}".format(uri))
        fname  = wget.download(uri)
        f = open(fname, mode='rb')
        content = f.read()
        f.close()
        os.unlink(fname)
        file_list = write_zip_content(content, out_path)
        return file_list

    if r.ok:
        file_list = write_zip_content(r.content, out_path)
    else:
        logger.error(f"Non-200 status code of {r.status_code} from {uri}")

    return file_list

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

def transform_opps(opps, out_path):
    """Transform the opportunity data to fit the SRT's schema
    
    Arguments:
        opps {dict} -- a dictionary containing the JSON response of get_opps()
    """
    transformed_opps = []
    for opp in opps:
        # logger.debug("transforming notice {}".format(opp[0]['_id']))
        schematized_opp = schematize_opp(opp)
        if not schematized_opp:
            continue
        url = schematized_opp.get('url','')
        opp_id = schematized_opp.pop('opp_id')
        file_list = get_docs(opp_id, out_path)
        if file_list:
            attachment_data = [get_attachment_data(f, url) for f in file_list]
            schematized_opp['attachments'].extend(attachment_data)
        transformed_opps.append(schematized_opp)
    return transformed_opps

def main():
    out_path = os.path.join(os.getcwd(), 'attachments')
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    opps = get_yesterdays_opps()
    if not opps:
        return []
    transformed_opps = transform_opps(opps, out_path)

    return transformed_opps

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    transformed_opps = main()
    