from datetime import datetime as dt
from datetime import timedelta
from io import BytesIO
import logging
import os
import sys
import zipfile
import csv
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import stat
from utils.db.db import Notice, Predictions, Solicitations
from utils.db.db_utils import fetch_notice_type_by_id
from sqlalchemy.sql.expression import func

import requests

from .request_utils import requests_retry_session, get_org_request_details

logger = logging.getLogger(__name__)


def get_org_info(org_id):
    uri, params = get_org_request_details()
    params.update({'fhorgid': org_id})
    try:
        with requests_retry_session() as session:
            r = session.get(uri, params=params, timeout=100)
    except Exception as e:
        logger.error(f"Exception {e} getting org info from {uri} with these params:\n\
                     {params}", exc_info=True)
        sys.exit(1)
    data = r.json()
    org_list = data['orglist']
    try:
        first_org_record = org_list[0]
    except IndexError:
        return '', ''
    agency = first_org_record.get('fhagencyorgname', '')
    office = first_org_record.get('fhorgname', '')

    return agency, office


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
    poc = opp_data.get('pointOfContacts')
    if not poc:
        emails = []
    else:
        emails = [p.get('email') for p in poc if p.get('email')]
    # classification_code = opp_data.get('classificationCode','')
    # will revisit to document missing "classification code"
    try:
        classification_code = opp_data.get('psc', '')[0].get('code', '')
    except IndexError:
        classification_code = 0
    naics = max([i for naics_list in
                 [i.get('code') for i in opp_data.get('naics', {})]
                 for i in naics_list], key=len)
    subject = opp_data.get('title', '').title()
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
    # opp_id = opp.get('opportunityId')
    opp_id = opp.get('_id')
    if not opp_id:
        logger.warning(f"No opp_id for {opp}")
        return

    # opp_data = opp.get('data')
    opp_data = opp
    if not opp_data:
        return

    # notice_type_code = opp_data.get('type')
    notice_type_code = opp_data.get('type')['value']

    # notice_type = get_notice_type(notice_type_code)
    notice_type = notice_type_code

    if not notice_type:
        return

    # org_id = opp_data.get('organizationId')


    organizationHierarchy = opp_data.get('organizationHierarchy')
    agency = office = ""
    if organizationHierarchy and isinstance(organizationHierarchy, list) and len(organizationHierarchy) > 0:
        agency =organizationHierarchy[0].get('name','')
        if len(organizationHierarchy) > 1:
            office = organizationHierarchy[1].get('name','')

    solicitation_number = opp_data.get('cleanSolicitationNumber', '')
    # agency, office = get_org_info(org_id)
    # agency = opp_data

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

        # naics_array = opp.get('data',{}).get('naics')
        naics_array = opp.get('naics', {})
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

def mark_solNum_as_inactive(session, solNum):
    try:
        session.query(Solicitations). \
            filter(Solicitations.solNum == solNum). \
            update({"active": False, "updatedAt": func.current_timestamp()}, synchronize_session='fetch')
        logger.info("Marking solicitation {} as inactive".format(solNum))
        session.execute(f"delete from \"Predictions\" where \"solNum\" = '{solNum}' ")
        logger.info(f"Deleted Prediction table entry from {solNum}.")
    except Exception as e:
        logger.error(f"Error: marking {solNum} as inactive. Exception: {e}", exc_info=True)

def mark_solNum_as_active(session, solNum):
    try:
        logger.info("Marking solicitation {} as active".format(solNum))
        sql = '''update solicitations set active = True, "updatedAt" = NOW() where "solNum" = '{}' '''.format(solNum)
        session.execute(sql)
        sql = '''update "Predictions" set active = True, "updatedAt" = NOW() where "solNum" = '{}' '''.format(solNum)
        session.execute(sql)
    except Exception as e:
        logger.error(f"Error: marking {solNum} as active. Exception: {e}", exc_info=True)

def update_notice_type_if_necessary(session, solNum, notice_type_string):
    n = session.query(Notice).\
        filter(Notice.solicitation_number == solNum).\
        order_by(Notice.date.desc()).\
        limit(1).\
        first()
    current_notice_type = fetch_notice_type_by_id(n.notice_type_id, session).notice_type
    if (current_notice_type != notice_type_string):
        # create a new notice record with the updated type
        insert_sql = f'''
            insert into notice (notice_type_id, solicitation_number, agency,
                   date, notice_data, compliant, "createdAt", "updatedAt", na_flag)
            select notice_type.id, solicitation_number, agency, NOW(), notice_data,
                   compliant, NOW(), NOW(), na_flag
            from notice
            join notice_type on notice_type.notice_type = '{notice_type_string}'
            where solicitation_number = '{solNum}'
            order by date desc
            limit 1
'''
        session.execute(insert_sql)
        logger.info(f"Updated notice type for {solNum}. It was {current_notice_type} and was changed to {notice_type_string}")
        session.execute(f"delete from \"Predictions\" where \"solNum\" = '{solNum}' ")
        logger.info(f"Deleted Prediction table entry from {solNum}.")
        return 1
    return 0 # did not update anything


def update_old_active_solicitations(session, stats, age_cutoff):
    solNumArray = get_all_solNum_from_prediction_table(session, age_cutoff)
    stats['total'] = len(solNumArray)
    logger.info(f"Found {stats['total']} solicitations to update")


    for solNum in solNumArray:
        logger.debug(" updated {}.  {}/{} done --  looking at (active) {} next ".format(stats['updated'], stats["examined"], stats["total"], solNum))
        data = get_sol_data_from_feed(solNum)
        stats['examined'] += 1
        if data == SAM_DATA_FEED_NO_MATCH:
            mark_solNum_as_inactive(session, solNum)
            stats['updated'] += 1
        else:
            if (data != False):
                stats['updated'] += update_notice_type_if_necessary(session, solNum, data["Type"])

    logger.info("Scan for inactive solicitations complete. {} solicitations examined and {} marked inactive ".format(stats['examined'], stats['updated']))

# Make sure that our old inactive solicitations are still inactive.  May be an edge case
# where a solNum pops back up in sam and we want to makes sure it is activated
def check_inactive_solicitations(session, stats, age_cutoff):
    solNumArray = get_all_inactive_solicitation_numbers(session, age_cutoff)
    stats['total'] += len(solNumArray)
    logger.info(f"Found {stats['total']} solicitations to update")

    for solNum in solNumArray:
        logger.debug(" updated {}.  {}/{} done --  looking at (inactive) {} next ".format(stats['updated'], stats["examined"], stats["total"], solNum))
        data = get_sol_data_from_feed(solNum)
        stats['examined'] += 1
        if data != SAM_DATA_FEED_NO_MATCH and data != False:
            mark_solNum_as_active(session, solNum)
            stats['updated'] += 1

    logger.info("Recheck of inactive solicitations complete. {} solicitations examined (total all scans) and {} updatd (total all scans) ".format(stats['examined'], stats['updated']))


def update_old_solicitations(session, age_cutoff=365):
    try:
        stats = {'examined': 0, 'updated': 0, 'total': 0}
        check_inactive_solicitations(session, stats, age_cutoff)
        update_old_active_solicitations(session, stats, age_cutoff)
        logger.info("Recheck of inactive solicitations complete. {} solicitations examined (total all scans) and {} updatd (total all scans) ".format(stats['examined'], stats['updated']))
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)

    return stats


SAM_DATA_FEED_ERROR = 0
SAM_DATA_FEED_DOWNLOADED = 1
SAM_DATA_FEED_EXISTED = 2
SAM_DATA_FEED_DEFAULT_FILENAME = '/tmp/ContractOpportunitiesFullCSV.csv'
SAM_DATA_FEED_NO_MATCH = 3
sam_df = None
def get_sol_data_from_feed(sol_number):
    import pandas as pd
    global sam_df
    if update_sam_data_feed() == SAM_DATA_FEED_ERROR:
        return False

    if sam_df is None:
        sam_df = pd.read_csv(SAM_DATA_FEED_DEFAULT_FILENAME, encoding='latin1')
        sam_df.columns = sam_df.columns.str.replace('#', 'Num')
        sam_df.columns = sam_df.columns.str.replace('$', 'Dollars')
        sam_df['ShortSolNum'] = sam_df.SolNum.apply(lambda x: str(x).replace("-", ""))


    match_df = sam_df[sam_df.ShortSolNum == sol_number]
    # print (match_df)
    max_date_index = 0
    if len(match_df) == 0:
        return SAM_DATA_FEED_NO_MATCH
    if len(match_df) > 1:
        max_date = None
        for i in range(0, len(match_df)):
            # date is in format 2020-10-20 03:04:05.123-4 - we don't care about fractional seconds
            d = str(match_df.iloc[i].PostedDate)[:19]
            d_obj = dt.strptime( d, '%Y-%m-%d %H:%M:%S')
            if (max_date is None or d_obj > max_date):
                max_date = d_obj
                max_date_index = i
        # print ("I got {} rows for {}.  The max index is {}".format(len(match_df), sol_number, max_date_index))


    match_dictionary = match_df.to_dict('records')[max_date_index]

    return match_dictionary

def update_sam_data_feed(filename=SAM_DATA_FEED_DEFAULT_FILENAME, force=False):
    def download_wait(path_to_downloads, timeout=60):
        seconds = 0
        while seconds < timeout:
            time.sleep(1)
            seconds += 1
            if os.path.isfile(path_to_downloads):
                break
        if seconds == timeout:
            return False
        return seconds

    home = os.environ.get("HOME")
    if home == "/":
        home = "/root"
    if not os.path.exists(home + "/Downloads"):
        os.makedirs(home + "/Downloads")
    download_location = home + "/Downloads/ContractOpportunitiesFullCSV.csv"

    if os.path.isfile(filename):
        age_of_file = time.time() - os.stat(filename)[stat.ST_MTIME]
        if age_of_file < 24 * 60 * 60:
            return SAM_DATA_FEED_EXISTED

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        chrome_prefs = {"download.default_directory": "/root/Downloads"}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}

        print("getting driver")

        driver = webdriver.Chrome(options=chrome_options)
        print("opening page")
        driver.get('https://beta.sam.gov/data-services/Contract%20Opportunities/datagov?privacy=Public')

        print("Waiting for page load")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'ContractOp')]")))

        print ("following link")
        link = driver.find_element_by_xpath("//a[contains(text(),'ContractOp')]")
        link.click()

        print ("checking agreement boxes")
        checkboxes = driver.find_elements_by_xpath("//input[@type='checkbox']")
        for el in checkboxes:
            el.click()

        print("ready for submission")
        submit_button = driver.find_element_by_xpath("//button[contains(.,'Submit')]")
        submit_button.click()

        print("Clicked submit")

        result = download_wait(download_location)



        print("File downloaded in {} seconds".format(result))

        if result:
            if os.path.isfile(filename):
                os.remove(filename)
            os.rename(download_location, filename)
            return SAM_DATA_FEED_DOWNLOADED

    except Exception as e:
        print(e)
        return SAM_DATA_FEED_ERROR
