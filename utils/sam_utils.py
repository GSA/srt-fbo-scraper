from datetime import datetime as dt
from datetime import timedelta
from io import BytesIO
import logging
import os
import re
import sys
import zipfile
import utils.db.db as db

from utils.db.db_utils import fetch_notice_type_by_id
import copy
from utils import get_opps
import utils.db.db_utils

import requests

from .request_utils import requests_retry_session

logger = logging.getLogger(__name__)

naics_code_prefixes = ('334111', '334118', '3343', '33451', '334516', '334614',
         '5112', '518', '54169', '54121', '5415', '54169', '61142')

# Any solicitation with a PSC code in this list will be downloaded.  Defaults to the empty list unless it is changed
psc_codes = []

def opportunity_filter_function(opp):
    logger.debug(f"Considering {opp['solicitationNumber']}  from {opp['postedDate']}")
    psc_match = opp['classificationCode'] in psc_codes
    naics_match = any(opp['naicsCode'].startswith(n) for n in naics_code_prefixes)

    opp['epa_psc_match'] = psc_match
    opp['naics_match'] = naics_match

    return psc_match or naics_match

def set_psc_code_download_list( codes ):
    psc_codes.clear()
    psc_codes.extend(codes)


def write_zip_content(content, out_path):
    """Writes the bytes content of a request for a zip archive to out_path
    
    Arguments:
        content {bytes} -- binary response content (i.e. r.content)
        out_path {str} -- directory to write zip files to 
    """
    textract_ext = ('.doc', '.docx', '.epub', '.gif', '.htm', '.html', '.odt', '.pdf', '.rtf', '.txt')
    z = zipfile.ZipFile(BytesIO(content))
    unzipped_file_list = z.filelist
    if not unzipped_file_list:
        # if the archive's corrupted, this list is empty
        return
    try:
        z.extractall(out_path)
    except RuntimeError:
        # occurs on password protected archives
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
                    # capturing as non-machine
                    file_list.append(file_out_path)
        except AttributeError:
            pass
    file_list = [os.path.join(out_path, os.path.basename(f)) for f in file_list]

    return file_list


def get_notice_data(opp_data, opp_id):
    poc = opp_data.get('pointOfContact', [])
    emails = [p.get('email') for p in poc if p.get('email')]


    classification_code = opp_data.get('classificationCode', '')


    naics = opp_data.get('naicsCode', '')
    subject = opp_data.get('title', '').title()
    url = opp_data.get('uiLink', '')
    set_aside = opp_data.get('typeOfSetAside', '')

    notice_data = {'classcod': classification_code,
                   'psc': classification_code,
                   'naics': naics,
                   'subject': subject,
                   'url': url,
                   'setaside': set_aside,
                   'emails': emails}

    return notice_data


def get_notice_type(notice_type_code):
    sam_nt_map = {'o': 'Solicitation',
                  'p': 'Presolicitation',
                  'k': 'Combined Synopsis/Solicitation'}
    sam_notice_type = sam_nt_map.get(notice_type_code, '').title()
    if not sam_notice_type:
        other_codes = {'r': 'Sources Sought',
                       'g': 'Sale of Surplus Property',
                       's': 'Special Notice',
                       'i': 'Intent to Bundle Requirements (DoD- Funded)',
                       'a': 'Award Notice',
                       'u': 'Justification and Authorization'}
        if notice_type_code not in other_codes:
            logger.warning(f"Found an unanticipated notice type with code: {notice_type_code}")
            return
        return
    return sam_notice_type


def schematize_opp(opp):
    opp_id = opp['solicitationNumber']
    if not opp_id:
        logger.warning(f"No solicitation number for {opp}")
        return

    opp_data = copy.deepcopy(opp)
    if not opp_data:
        return

    # notice_type_code = opp_data.get('type')
#    notice_type_code = opp_data.get('type')['value']

    # notice_type = get_notice_type(notice_type_code)
    notice_type = opp_data['type']

    if not notice_type:
        return

    # org_id = opp_data.get('organizationId')

    # opp_data['fullParentPathName'] is a . separated list. First is the agency, second is the office, and then it goes down from there.
    organizationHierarchy = opp_data['fullParentPathName'].split(".")
    agency = office = ""
    if organizationHierarchy and isinstance(organizationHierarchy, list) and len(organizationHierarchy) > 0:
        agency =organizationHierarchy[0]
        if len(organizationHierarchy) > 1:
            office = organizationHierarchy[1]

    solicitation_number = opp['solicitationNumber']
    # agency, office = get_org_info(org_id)
    # agency = opp_data

    required_data = {'notice type': notice_type,
                     'solnbr': solicitation_number,
                     'agency': agency,
                     'compliant': 0,
                     'office': office,
                     'attachments': []}

    notice_data = get_notice_data(opp_data, opp_id)

    schematized_opp = {**opp_data, **required_data, **notice_data}
    schematized_opp['opp_id'] = opp_id

    return schematized_opp

_total_skipped = 0
_total_kept = 0
def sol_type_filter(opps, types):
    """
    Filter out any solicitaitons that aren't the correct type.  We are only interested in
    Args:
        opps list of solicitations
        types list of allows sol types

    Returns:
        list of solicitations that have the correct type.
    """
    global _total_skipped, _total_kept
    filtered_opps = []
    for opp in opps:
        if opp['type']['value'] in types:
            filtered_opps.append(opp)
            _total_kept += 1
        else:
            _total_skipped += 1

    logger.debug("Total skip stats so far: Skipping {} out of {} due to solicitation type".format(_total_skipped, _total_kept + _total_skipped))
    return filtered_opps

def naics_filter(opps):
    """Filter out opps without desired naics
    
    Arguments:
        opps {list} -- a list of sam opportunity api results
        naics {list} -- a list of naics to filter with
    
    Returns:
        [list] -- a subset of results with matching naics
    """
    naics = naics_code_prefixes
    filtered_opps = []
    for opp in opps:

        # naics_array = opp.get('data',{}).get('naics')
        if 'naics' in opp:
            naics_array = opp.get('naics', {})
        elif 'naicsCode' in opp:
            naics_array = [ {'code': opp['naicsCode']} ]

        if not naics_array:
            continue
        nested_naics_codes = [c for c in [d.get('code', []) for d in naics_array]]
        # opp_naics = [i for sublist in nested_naics_codes for i in sublist]
        opp_naics = [i for i in nested_naics_codes]
        for c in opp_naics:
            if any(c.startswith(n) for n in naics):
                filtered_opps.append(opp)
                break
    return filtered_opps


def get_dates_from_opp(opp):
    mod_date = opp.get('modifiedDate', '')
    if "T" in mod_date:
        modified_date = mod_date.split('T')[0]
    else:
        modified_date = mod_date.split(' ')[0]
    # post_date = opp.get('postedDate','')
    post_date = opp.get('publishDate', '')
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

    # the entries are ordered by date so once it gets past yesterday we can stop
    dateStr = opps[-1:][0]['modifiedDate'][0:10]
    modDate = dt.strptime(dateStr, '%Y-%m-%d')
    if modDate < get_day('yesterday'):
        is_more_opps = False
    else:
        is_more_opps = True

    return yesterdays_opps, is_more_opps

def get_all_inactive_solicitation_numbers(session, age_cutoff=365):
    sql = '''
        select "solNum" from "solicitations"
    where not active and
         greatest("createdAt", "updatedAt") > CURRENT_DATE - interval '{}' day
    order by "updatedAt" desc
        '''.format(age_cutoff)
    logger.debug("Gathering solicitation numbers that match SQL: {}".format(sql))
    result = session.execute(sql)
    solNumArray = [x.solNum for x in result]
    return solNumArray


def get_all_solNum_from_prediction_table(session, age_cutoff=90):
    sql = '''
        select "Predictions"."solNum", greatest("Predictions"."createdAt", "Predictions"."updatedAt") as last_touch
    from "Predictions"
             join solicitations on "Predictions"."solNum" = solicitations."solNum"
    where greatest("Predictions"."createdAt", "Predictions"."updatedAt") > CURRENT_DATE - interval '{}' day and
       (solicitations.active)
    order by last_touch desc
        '''.format(age_cutoff)
    logger.debug("Gathering solicitation numbers that match SQL: {}".format(sql))
    result = session.execute(sql)
    solNumArray = [x.solNum for x in result]
    return solNumArray






def update_notice_type_if_necessary(sol, sam_data,session):
    '''
    Looks at the notice type in the solicitation and updates it to the sam_data value if necesary
    Args:
        sol: sqlalchemy Solicitation
        sam_data: sam data from the sam.gov API
        session: open db session

    Returns: the number of solicitations updated. (so either 1 or 0)
    '''
    if sol.noticeType != sam_data['type']:
        logger.info(f"Updating the notice type for {sol.solNum} to be {sam_data['type']}")
        sol.noticeType = sam_data['type']
        sol.notice_type_id = utils.db.db_utils.fetch_notice_type_id(sam_data['type'], session)
        return 1
    return 0

def update_old_solicitations(session, age_cutoff=365, max_tests=100, fraction=14, noticeTypes=("Solicitation", "Combined Synopsis/Solicitation")):
    '''
    Examines a fraction of the existing solicitations newer than the age cutoff to see if there
    are any changes in sam.gov. If you call this function every day and you don't hit the max_tests
    limit, you will re-check each solicitiaton every $fraction days.

    Args:
        session: open db session
        age_cutoff: how many days to look back
        max_tests: at most test this many solicitaitons so we don't go over our api call limit

    Returns:

    '''
    try:
        stats = {'examined': 0, 'updated': 0, 'total': 0}

        solicitations = session.query(db.Solicitation).filter(db.Solicitation.active == True).filter(db.Solicitation.date > dt.today() - timedelta(age_cutoff)).order_by(db.Solicitation.date.desc())
        candidate_solicitations = []
        for sol in solicitations:
            if sol.id % fraction == 0:
                if sol.noticeType in noticeTypes:
                    candidate_solicitations.append(sol)

        for sol in candidate_solicitations:
            stats['examined'] += 1
            if stats['examined'] > max_tests:
                logger.warning("Max test count hit when trying to examine old solicitations")
                break;

            sam_sol_data = get_opps.get_opp_from_sam(sol.solNum)
            if sam_sol_data == None:
                logger.info(f"could not find {sol.solNum} in the sam.gov API - I will assume that means it is inactive")
                sol.active = False
                stats['updated'] += 1
                continue

            if sol.active != ( sam_sol_data['active'].lower() == "yes") :
                sol.active = sam_sol_data['active']
                logger.info(f"Updating the active state for {sol.solNum} - setting it inactive")
                stats['updated'] += 1
            else:
                logger.debug(f"Performed check on {sam_sol_data['solicitationNumber']} but no updates were necessary")

            stats['updated'] += update_notice_type_if_necessary(sol, sam_sol_data, session)

        logger.info("Recheck of old solicitations complete. {} solicitations examined and {} updated ".format(stats['examined'], stats['updated']))
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)

    return stats
