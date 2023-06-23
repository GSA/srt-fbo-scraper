import json
import logging
import sys


import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager

logger = logging.getLogger(__name__)

class SAMHttpAdapter(HTTPAdapter):
    """
    Transport adapter that allows us to use custom ssl_context for SAM API
    https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled/71646353#71646353
    """
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)



def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504), session=None
):
    """
    Use to create an http(s) requests session that will retry a request.
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    # Work around for https://bugs.python.org/issue44888
    ctx.options |= 0x4
    session.mount('https://', SAMHttpAdapter(ctx))

    return session


def get_opps(uri, params, headers, session=None):
    try:
        logger.info(
            "Fetching {} with params {} and headers {}".format(uri, params, headers)
        )
        r = requests_retry_session(session=session).get(
            uri, params=params, timeout=100, headers=headers
        )
    except Exception as e:
        logger.critical(f"Exception {e} getting opps from {uri}", exc_info=True)
        sys.exit(1)
    data = r.json()
    try:
        opps = data["_embedded"]["results"]
        total_pages = data["page"]["totalPages"]
    except KeyError as e:
        error_message = data.get("errormessage", "")
        data_str = json.dumps(data)
        if "request's IP does not match any pattern" not in error_message:
            logger.error(f"Confirm API stability:\n{data_str}")
        else:
            logger.error(f"{e}: making request to {uri}:\n{data_str}")
        return None, None

    return opps, total_pages
