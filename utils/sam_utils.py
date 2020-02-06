from datetime import datetime as dt
from datetime import timedelta
from io import BytesIO
import logging
import os
import sys
import zipfile

import requests

from .request_utils import requests_retry_session, get_org_request_details

logger = logging.getLogger(__name__)

def get_org_info(org_id):
    uri, params = get_org_request_details()
    params.update({'fhorgid':org_id})
    try:
        with requests_retry_session() as session:
            r = session.get(uri, params = params, timeout = 100)
    except Exception as e:
        logger.error(f"Exception {e} getting org info from {uri} with these params:\n\
                     {params}", exc_info=True)
        sys.exit(1)
    data = r.json()
    org_list = data['orglist']
    try:
        first_org_record = org_list[0]
    except IndexError:
        return '',''
    agency = first_org_record.get('fhagencyorgname','')
    office = first_org_record.get('fhorgname','')
    
    return agency, office

def write_zip_content(content, out_path):
    """Writes the bytes content of a request for a zip archive to out_path
    
    Arguments:
        content {bytes} -- binary response content (i.e. r.content)
        out_path {str} -- directory to write zip files to 
    """
    textract_ext = ('.doc','.docx','.epub','.gif','.htm','.html','.odt','.pdf','.rtf','.txt')
    z = zipfile.ZipFile(BytesIO(content))
    unzipped_file_list = z.filelist
    if not unzipped_file_list:
        #if the archive's corrupted, this list is empty
        return
    try:
        z.extractall(out_path)
    except RuntimeError:
        #occurs on password protected archives
        return
    file_list = []
    for f in unzipped_file_list:
        try:
            file_name = f.filename
            if not file_name.endswith('/'):
                file_out_path = os.path.join(out_path, file_name)
                if file_out_path.endswith(textract_ext):
                    file_list.append(file_out_path)
                else:
                    #capturing as non-machine
                    file_list.append(file_out_path)
        except AttributeError:
            pass
    file_list = [os.path.join(out_path, os.path.basename(f)) for f in file_list]

    return file_list

def get_notice_data(opp_data, opp_id):
    poc = opp_data.get('pointOfContacts')
    if not poc:
        emails = []
    else:
        emails = [p.get('email') for p in poc if p.get('email')]
    #classification_code = opp_data.get('classificationCode','')
    # will revisit to document missing "classification code"
    try:
        classification_code = opp_data.get('psc','')[0].get('code','')
    except IndexError:
        classification_code = 0
    naics = max([i for naics_list in 
                [i.get('code') for i in opp_data.get('naics',{})] 
                for i in naics_list], key = len)
    subject = opp_data.get('title','').title()
    url = f'https://beta.sam.gov/opp/{opp_id}/view'
    # set_aside = opp_data.get('solicitation',{}).get('setAside','')
    set_aside = opp_data.get('typeOfSetAside', '')

    notice_data = {'classcod': classification_code,
                   'naics': naics,
                   'subject': subject,
                   'url': url,
                   'setaside': set_aside,
                   'emails': emails}

    return notice_data 

def get_notice_type(notice_type_code):
    sam_nt_map = {'o':'Solicitation',
                  'p':'Presolicitation',
                  'k':'Combined Synopsis/Solicitation'}
    sam_notice_type = sam_nt_map.get(notice_type_code, '').title()
    if not sam_notice_type:
        other_codes = {'r':'Sources Sought',
                       'g':'Sale of Surplus Property',
                       's':'Special Notice',
                       'i':'Intent to Bundle Requirements (DoD- Funded)',
                       'a':'Award Notice',
                       'u':'Justification and Authorization'}
        if notice_type_code not in other_codes:
            logger.warning(f"Found an unanticipated notice type with code: {notice_type_code}")
            return
        return
    return sam_notice_type

def schematize_opp(opp):
    #opp_id = opp.get('opportunityId')
    opp_id = opp.get('_id')
    if not opp_id:
        logger.warning(f"No opp_id for {opp}")
        return

    #opp_data = opp.get('data')
    opp_data = opp
    if not opp_data:
        return

    #notice_type_code = opp_data.get('type')
    notice_type_code = opp_data.get('type')['value']

    #notice_type = get_notice_type(notice_type_code)
    notice_type = notice_type_code

    if not notice_type:
        return
    
    #org_id = opp_data.get('organizationId')


    agency =opp_data.get('organizationHierarchy','')[0].get('name','')
    office =opp_data.get('organizationHierarchy','')[1].get('name','')

    solicitation_number = opp_data.get('cleanSolicitationNumber','')
    #agency, office = get_org_info(org_id)
    #agency = opp_data
    
    required_data = {'notice type': notice_type,
                     'solnbr': solicitation_number,
                     'agency': agency,
                     'compliant': 0,
                     'office': office,
                     'attachments': []}
    
    notice_data = get_notice_data(opp_data, opp_id)

    schematized_opp = {**required_data, **notice_data}
    schematized_opp['opp_id'] = opp_id
    
    return schematized_opp

def naics_filter(opps):
    """Filter out opps without desired naics
    
    Arguments:
        opps {list} -- a list of sam opportunity api results
        naics {list} -- a list of naics to filter with
    
    Returns:
        [list] -- a subset of results with matching naics
    """
    naics = ('334111', '334118', '3343', '33451', '334516', '334614', 
             '5112', '518', '54169', '54121', '5415', '54169', '61142')
    filtered_opps = []
    for opp in opps:

        #naics_array = opp.get('data',{}).get('naics')
        naics_array = opp.get('naics',{})
        if not naics_array:
            continue
        nested_naics_codes = [c for c in [d.get('code',[]) for d in naics_array]]
        #opp_naics = [i for sublist in nested_naics_codes for i in sublist]
        opp_naics = [i for i in nested_naics_codes ]
        for c in opp_naics:
            if any(c.startswith(n) for n in naics):
                filtered_opps.append(opp)
                break
    return filtered_opps

def get_dates_from_opp(opp):
    mod_date = opp.get('modifiedDate','')
    if "T" in mod_date:
        modified_date = mod_date.split('T')[0]
    else:
        modified_date = mod_date.split(' ')[0]
    #post_date = opp.get('postedDate','')
    post_date = opp.get('publishDate','')
    if "T" in post_date:
        posted_date = post_date.split('T')[0]
    else:
        posted_date = post_date.split(' ')[0]
    posted_date_dt = None
    modified_date_dt = None
    try:
        modified_date_dt = dt.strptime(modified_date, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        posted_date_dt = dt.strptime(posted_date, "%Y-%m-%d")
    except ValueError:
        pass
            
    return modified_date_dt, posted_date_dt

def get_day(today_or_yesterday):
    if today_or_yesterday == 'today':
        day = dt.strptime(dt.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    elif today_or_yesterday == 'yesterday': 
        day = dt.strptime((dt.today() - timedelta(1)).strftime("%Y-%m-%d"), "%Y-%m-%d")
    
    return day

def find_yesterdays_opps(opps):
    yesterday = get_day('yesterday')
    today = get_day('today')
    yesterdays_opps = []
    todays_opps = []
    for i, opp in enumerate(opps):
        modified_date_dt, posted_date_dt = get_dates_from_opp(opp)
        is_mod_yesterday = modified_date_dt == yesterday
        is_mod_today = modified_date_dt == today
        try:
            is_post_yesterday = posted_date_dt == yesterday
            is_post_today = posted_date_dt == today
        except:
            # some notices don't provide one of these dates, and we shouldn't guess
            pass
        if is_mod_yesterday or is_post_yesterday:
            yesterdays_opps.append(opp)
        elif is_mod_today or is_post_today:
            todays_opps.append(opp)
        else:
            pass
    n_today_opps = len(todays_opps)
    n_yesterday_opps = len(yesterdays_opps)

    is_today_and_yesterday_opps = (n_today_opps + n_yesterday_opps) == len(opps)
    is_only_todays_opps = True if n_today_opps == len(opps) else False
    is_only_yesterdays_opps = True if n_yesterday_opps == len(opps) else False
    is_more_opps = is_only_todays_opps or is_only_yesterdays_opps or is_today_and_yesterday_opps
    
    return yesterdays_opps, is_more_opps
