import json
import logging
import os
import sys
from random import randint



import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def requests_retry_session(retries=3, 
                           backoff_factor=0.3,
                           status_forcelist=(500, 502, 503, 504), 
                           session=None):
    '''
    Use to create an http(s) requests session that will retry a request.
    '''
    session = session or requests.Session()
    retry = Retry(total = retries, 
                  read = retries, 
                  connect = retries, 
                  backoff_factor = backoff_factor, 
                  status_forcelist = status_forcelist)
    adapter = HTTPAdapter(max_retries = retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session


def get_opps(uri, params, headers, session = None):
    try:
        logger.info("Fetching {} with params {} and headers {}".format(uri, params, headers))
        r = requests_retry_session(session=session).get(uri, params = params, timeout = 100, headers = headers)
    except Exception as e:
        logger.critical(f"Exception {e} getting opps from {uri}", exc_info=True)
        sys.exit(1)
    data = r.json()
    try:
        opps = data['_embedded']['results']
        total_pages = data['page']['totalPages']
    except KeyError as e:
        error_message = data.get('errormessage','')
        data_str = json.dumps(data)
        if not "request's IP does not match any pattern" in error_message:
            logger.error(f"Confirm API stability:\n{data_str}")
        else:
            logger.error(f"{e}: making request to {uri}:\n{data_str}")
        return None, None

    return opps, total_pages


