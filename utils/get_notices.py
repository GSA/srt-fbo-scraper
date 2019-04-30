import random
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()
import sys
import zipfile
import logging
import requests
import os

logger = logging.getLogger(__name__)
SAM_API_KEY = os.getenv('SAM_API_KEY')
if not SAM_API_KEY:
    logger.critical("SAM_API_KEY not in env.")
    sys.exit(1)

def xstr(s):
    """[Converts objects to strings, treting NoneTypes as empty strings. Useful for dict.get() return values.]
    
    Arguments:
        s {[obj]} -- [any python object that can be converted to a string]
    
    Returns:
        [str] -- [s as a string.]
    """
    if s is None:
        return ''
    else:
        return str(s)


def get_random(n = 13):
    """[Generate a random string of n digits, with the first digit not equal to 0.]
    
    Keyword Arguments:
        n {int} -- [number of digits in randomly generated string] (default: {13})
    
    Returns:
        [str] -- [a string of n randomly generate integers]
    """
    start_n = str(random.randint(1,9))
    for _ in range(n-1):
        start_n += str(random.randint(0,9))
    return start_n


def get_now_minus_n(n):
    """[Returns a datetime string from n days ago, appended with '-04:00']
    
    Arguments:
        n {[int]} -- [the number of days to go back to]
    
    Returns:
        [str] -- [now_minus_n is a string representing a date n days ago]
    """
    now_minus_n = datetime.utcnow() - timedelta(n)
    now_minus_n = now_minus_n.strftime('%Y-%m-%d')
    #this is always appended to the time param for some reason, so we'll manually append it here
    now_minus_n += '-04:00'
    return now_minus_n


def api_get(uri, payload):
    """[requests.get wrapper with error handling that returns the json]
    
    Arguments:
        uri {[str]} -- [the uri to request]
        payload {[dict]} -- [a dict of params for the GET]
    
    Returns:
        [data] -- [dict, json-like]
    """
    try:
        #the headers dict will be merged with the default/session headers
        page = payload.get('page', 0)
        headers = {'origin': 'https://beta.sam.gov',
                   'referer': f'https://beta.sam.gov/search?keywords=&sort=-modifiedDate&index=opp&is_active=true&page={page}'}
        r = requests.get(uri, params = payload, headers = headers)
    except Exception as e:
        logger.critical(f"Exception in `get_opportunities` making GET request to {uri} with {payload}: \
                          {e}", exc_info=True)
        return
    if r.status_code != 200:
        logger.critical(f"Exception in `get_opportunities` making GET request to {uri} with {payload}: \
                        non-200 status code of {r.status_code}")
        return
    data = r.json()
    
    return data
    

def get_opportunities(modified_date = None, 
                      notice_types = ['p', 'k', 'm'],
                      naics = ['334111', '334118', '3343', '33451', '334516', '334614', 
                              '5112', '518', '54169', '54121', '5415', '54169', '61142']):
    '''
    [Makes a GET request to the Get Opportunities API for a given procurement type (p_type) and date range.]
    
    Arguments:
        p_type (str): The procurement type. Valid values include:
                            u = Justification (J&A)
                            p = Pre solicitation
                            a = Award Notice
                            r = Sources Sought
                            s = Special Notice
                            g = Sale of Surplus Property
                            k = Combined Synopsis/Solicitation
                            i = Intent to Bundle Requirements (DoDFunded)
                            m = Modification
                            Note: Below services are now retired:
                            f = Foreign Government Standard
                            l = Fair Opportunity / Limited Sources
                            Use Justification (u) instead of fair
                            Opportunity
        modified_date (str): [Format must be '%Y-%m-%d'. If None, defaults to three days ago.]
        
    Returns:
        data (dict): [the json response. See the API documentation for more detail.]
    '''
    modified_date_formatted = f'{modified_date}-04:00'
    modified_date = modified_date_formatted if modified_date else get_now_minus_n(3)
    payload = {'api_key': SAM_API_KEY,
               'random': get_random(),
               'index': 'opp',
               'q':'',
               'is_active': 'true',
               'page':'0',
               'notice_type': ",".join(notice_types),
               'modified_date': modified_date,
              }
    if naics:
        payload.update({'naics': ",".join(naics)})
    uri = 'https://api.sam.gov/prod/sgs/v1/search/'
    data = api_get(uri, payload)
    if not data:
        return
    try:
        results = data['_embedded']['results']
    except KeyError:
        #no results!
        return
    total_pages = data['page']['totalPages']
    page = 1
    while page < total_pages:
        print("*"*80)
        payload.update({'page': page})
        _data = api_get(uri, payload)
        if not _data:
            page += 1
            continue
        _results = _data['_embedded']['results']
        results.extend(_results)
        page += 1
        
    return results

def get_date_and_year(modified_date):
    """[Given the modifiedDate value in the API response, get the mmdd and yy values]
    
    Arguments:
        modified_date {[str]} -- [description]
    
    Returns:
        [tup] -- [tuple containing the date (mmdd) and year (yy) as strings]
    """
    modified_date_t_index = modified_date.find("T")
    date = modified_date[5:modified_date_t_index].replace("-",'')
    year = modified_date[2:4]
    return date, year

def proper_case(string):
    """[Given a string that's supposed to be a an agencys name (i.e. a proper noun), case it correctly.]
    
    Arguments:
        string {[str]} -- [a string of an agency's name, e.g. DEPARTMENT OF HOUSING AND URBAN DEVELOPMENT]
    
    Returns:
        [str] -- [string_proper, the proper-cased string, e.g. Department of Housing and Urban Development]
    """
    string_split = string.lower().split()
    string_proper = ''
    dont_caps = {'the', 'of', 'and'}
    for word in string_split:
        if word not in dont_caps:
            string_proper += f'{word.capitalize()} '
        else:
            string_proper += f'{word} '
    string_proper = string_proper.strip()
    
    return string_proper


def parse_agency_name(agency):
    """Convert the awkward agency string formats (e.g. HOMELAND SECURITY, DEPARTMENT OF --> Department of Homeland Security)
    
    Arguments:
        agency {[str]} -- [an agency's name]
    
    Returns:
        [str] -- [agency_name_proper, the proper-cased and formatted name of the agency]
    """
    agency = agency.strip()
    if not agency.isupper():
        return agency
    try:
        comma_index = agency.index(",")
    except ValueError:
        #because there's no comma
        agency = proper_case(agency)
        return agency
    agency_name = f'{agency[comma_index+2:]} {agency[:comma_index]}'.lower()
    agency_name_proper = proper_case(agency_name)
    
    return agency_name_proper


def get_agency_office_location_zip_offadd(organization_hierarchy):
    """[Extract geodata for the organizationHierarchy field of the api response]
    
    Arguments:
        organization_hierarchy {[list]} -- [a list of dictionaries (json array)]
    
    Returns:
        [tuple] -- [returns agency, office, location, zip_code, and offadd strings]
    """
    agency = ''
    office = ''
    location = ''
    zip_code = ''
    offadd = ''
    for i in organization_hierarchy:
        level = i.get('level')
        if level == 1:
            agency = xstr(i.get('name',''))
            agency = xstr(parse_agency_name(agency))
        elif level == 2:
            office = xstr(parse_agency_name(i.get('name','')))
        else:
            location = xstr(i.get('name'))
            address = i.get('address')
            if not address:
                continue
            zip_code = xstr(address.get('zip', ''))
            street_address = xstr(address.get('streetAddress', ''))
            street_address2 = xstr(address.get('streetAddress2', ''))
            city = xstr(address.get('city', ''))
            state = xstr(address.get('state', ''))
            offadd = f'{street_address} {street_address2} {city}, {state}'
            offadd = '' if offadd == '  , ' else offadd
            offadd = re.sub(r'  +',' ', offadd)

    return agency, office, location, zip_code, offadd

def get_classcod_naics(psc_naics):
    if not psc_naics:
        return ''
    classcod_naics = max([i.get('code') for i in psc_naics], key = len)
    
    return classcod_naics
 
def get_respdate(response_date):
    if not response_date:
        return ''
    try:
        respdate = datetime.fromisoformat(response_date).strftime('%m%d%y')
    except ValueError as e:
        logger.warning(f"Error {e} parsing response_date of {response_date}", exc_info = True)
        return ''
    
    return respdate

def get_contact(point_of_contacts):
    if not point_of_contacts:
        return ''
    titles = [poc.get('title', ' ') for poc in point_of_contacts]
    try:
        contact = " ".join(titles)
    except TypeError:
        #occurs because titles is [None]
        return ''

    return contact

def get_description(descriptions):
    if not descriptions:
        return ''
    last_modified_dates = []
    for d in descriptions:
        last_modified_date = d.get('lastModifiedDate')
        if not last_modified_date:
            continue
        try:
            last_modified_date = datetime.fromisoformat(last_modified_date)
            last_modified_dates.append(last_modified_date)
        except ValueError as e:
            logger.warning(f"Error {e} parsing last_modified_date of {last_modified_date}", exc_info = True)
            continue
    max_date = max(last_modified_dates)
    max_date_i = last_modified_dates.index(max_date)
    description = descriptions[max_date_i].get('content','')
    
    return description
        
def get_text_from_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    # get text
    text = soup.get_text(separator = ' ')
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

def get_setasides(setasides):
    setaside = ''
    if not setasides:
        setaside = 'N/A'
        return setaside
    
    if isinstance(setasides, list):
        for s in setasides:
            if not s:
                continue
            setaside += s.get('value', '') + ' '
        
    else:
        #must be a single dict
        setaside = setasides.get('value', '')
    setaside = setaside.strip()
    if not setaside:
        #empty strings are Falsy
        setaside = 'N/A'
    
    return setaside


def get_place_of_performance(place_of_performance):
    if not place_of_performance:
        return '','',''
    try:
        d = place_of_performance[0]
    except IndexError:
        return '','',''
    popzip = xstr(d.get('zip', ''))
    popcountry = xstr(d.get('country', ''))
    city = xstr(d.get('city', ''))
    street_address = xstr(d.get('streetAddress', ''))
    street_address2 = xstr(d.get('streetAddress2', ''))
    state = xstr(d.get('state', ''))
    popaddress = f'{street_address} {street_address2} {city}, {state}'
    popaddress = '' if popaddress == '  , ' else popaddress
    popaddress = re.sub(r'  +',' ', popaddress)
    
    return popzip, popcountry, popaddress   
        

def extract_emails(res):
    '''
    Given a json string representing a single opportunity notice, use an email re to find all the contact emails.
    
    Parameters:
        dumped_res (str): the result of json.dumps()
        
    Returns:
        emails (list): a list of unique email addresses
    '''
    email_re = re.compile(r'([0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*@([0-9a-zA-Z][-\w]*[0-9a-zA-Z]\.)+[a-zA-Z]{2,9})')
    pocs = res.get('pointOfContacts')
    descriptions = res.get('descriptions')
    text_to_search = f'{pocs} {descriptions}'
    all_matches = re.findall(email_re, text_to_search)
    matches = [max(tup, key = len) for tup in all_matches]
    emails = list(set(matches))
    
    return emails
    

def schematize_results(results):
    '''
    Givent the results of the Get Opportunities API, convert the json to SRT's schema
    '''
    notice_data = {'PRESOL': [],
                   'COMBINE': [],
                   'MOD': []}
    if not results:
        return []
    for res in results:
        is_canceled = res.get('isCanceled')
        if is_canceled:
            continue
        modified_date = res['modifiedDate']
        date, year = get_date_and_year(modified_date)
        organization_hierarchy = res['organizationHierarchy']
        place_of_performance = res.get('placeOfPerformance', '')
        popzip, popcountry, popaddress = get_place_of_performance(place_of_performance)
        agency, office, location, zip_code, offadd = get_agency_office_location_zip_offadd(organization_hierarchy)
        psc = res.get('psc')
        classcod = get_classcod_naics(psc)
        _naics = res.get('naics')
        naics = get_classcod_naics(_naics)
        subject = res.get('title', '')
        solnbr = res.get('solicitationNumber').lower().strip()
        response_date = res.get('responseDate')
        respdate = get_respdate(response_date)
        archive_date = res.get('archiveDate')
        archdate = get_respdate(archive_date)
        point_of_contacts = res.get('pointOfContacts')
        contact = get_contact(point_of_contacts)
        descriptions = res.get('descriptions')
        desc = get_text_from_html(get_description(descriptions))
        _id = res.get('_id')
        url = f'https://beta.sam.gov/opp/{_id}'
        setasides = res.get('solicitation').get('setAside')
        setaside = get_setasides(setasides)
        notice = {'date': date,
                 'year': year,
                 'agency': agency,
                 'office': office,
                 'location': location,
                 'zip': zip_code,
                 'classcod': classcod,
                 'naics': naics,
                 'offadd': offadd,
                 'subject': subject,
                 'solnbr': solnbr,
                 'respdate': respdate,
                 'archdate': archdate,
                 'contact': contact,
                 'desc': desc,
                 'url': url,
                 'setaside': setaside,
                 'popzip': popzip,
                 'popcountry': popcountry,
                 'popaddress': popaddress
                 }
        emails = extract_emails(res)
        notice.update({'emails': emails})
        notice_type = res.get('type').get('value')
        if notice_type == 'Combined Synopsis/Solicitation':
            notice_data['COMBINE'].append(notice)
        elif notice_type == 'Presolicitation':
            notice_data['PRESOL'].append(notice)
        elif notice_type == 'Modification/Amendment/Cancel':
            notice_data['MOD'].append(notice)
        else:
            logger.warning("Found an unanticipated notice type of {notice_type}")
            
    return notice_data
            
def get_notices(modified_date = None):
    results = get_opportunities(modified_date = modified_date)
    notices = schematize_results(results)
    
    return notices

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    notices = get_notices()