import logging
import os
import random
import sys
import zipfile

import requests
import textract

logger = logging.getLogger(__name__)
SAM_API_KEY = os.getenv('SAM_API_KEY')
if not SAM_API_KEY:
    logger.critical("SAM_API_KEY not in env.")
    sys.exit(1)


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

def attachments_get(notice_id, solicitation_number):
    uri = 'https://api.sam.gov/prod/opps/v1/opportunities/attachments'
    referer = f'https://beta.sam.gov/opp/{notice_id}?keywords={solicitation_number}&sort=-relevance&index=opp&is_active=true&page=1&inactive_filter_values=false&date_filter_index=0&date_rad_selection=dateRange'
    payload = {'api_key': SAM_API_KEY,
               'random': get_random(),
               'noticeIds': notice_id,
              }
    try:
        headers = {'origin': 'https://beta.sam.gov',
                   'referer': referer}
        r = requests.get(uri, params = payload, headers = headers)
    except Exception as e:
        logger.critical(f"Exception in `get_opportunities` making GET request to {uri} with {payload}: \
                          {e}", exc_info=True)
        return
    if r.status_code == 404:
        #404's occur when there aren't any attachments
        return
    if r.status_code != 200:
        logger.critical(f"Exception in `get_opportunities` making GET request to {uri} with {payload}: \
                        non-200 status code of {r.status_code}")
        return
    attachment_data = r.json()
    
    return attachment_data


def get_notice_cookies(referer):
    r = requests.get(referer)
    cookies = r.cookies.get_dict()
    citrix_ns_id = cookies.get('citrix_ns_id', '')
    wlf = cookies.get('citrix_ns_id_.sam.gov_%2F_wlf', '')
    cookie_string = f'citrix_ns_id={citrix_ns_id}; citrix_ns_id_.sam.gov_%2F_wlf={wlf}'
    
    return cookie_string


def get_notice_file(notice_id, resource_id):
    referer = f'https://beta.sam.gov/opp/{notice_id}'
    cookie_string = get_notice_cookies(referer)
    file_uri = f'https://api.sam.gov/prod/opps/v1/opportunities/resources/files/{resource_id}'
    headers = {'Cookies': cookie_string,
               'Host': 'api.sam.gov',
               'Referer': referer,
               'Upgrade-Insecure-Requests': '1'}
    payload = {'api_key': SAM_API_KEY}
    try:
        r = requests.get(file_uri, headers = headers, params = payload)
    except Exception as e:
        logger.critical(f"Exception {e} in `get_notice_file` making GET request to {file_uri} with headers: {headers}", exc_info=True)
        return None, file_uri
    if r.status_code != 200:
        request_content = None
    else:
        request_content = r.content
    
    return request_content, file_uri
       

def write_file(request_content, out_path, file_name):
    file_out_path = os.path.join(out_path, file_name)
    with open(file_out_path, 'wb') as f:
        f.write(request_content)
    
    return file_out_path


def handle_zips(zip_file, out_path):
    unzipped_files = []
    zip_file_basename = os.path.basename(zip_file)
    target_dir = zip_file_basename.replace('.zip', '')
    target_dir = os.path.join(out_path, target_dir)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(target_dir)
        zip_file_list = zip_ref.filelist
        for z in zip_file_list:
            try:
                zip_file_name = z.filename
                if not zip_file_name.endswith('/'):
                    file_out_path = os.path.join(out_path, target_dir, zip_file_name)
                    unzipped_files.append(file_out_path)
            except AttributeError:
                pass
    
    return unzipped_files
        

def textract_attachment(attachment_data, notice_id, out_path):
    attachments = []
    resources = attachment_data.get('resources')
    for resource in resources:
        content_length = int(resource.get('size', 1))
        if content_length > 5e8:
            #If the file is greater than 500MB, skip it
            continue
        resource_id = resource.get('resourceId')
        file_name = resource.get('uri')
        request_content, file_uri = get_notice_file(notice_id, resource_id)
        if not request_content:
            #If the request for the file failed, capture that as a non-machine-readable file
            attachment = {'filename': f'{file_uri}api_key={SAM_API_KEY}',
                          'machine_readable': False,
                          'attachment_text': '',
                          'attachment_url': f'{file_uri}api_key={SAM_API_KEY}'}
            attachments.append(attachment)
            continue
        file_out_path = write_file(request_content, out_path, file_name)
        files_to_textract = []
        if file_out_path.endswith('.zip'):
            unzipped_files = handle_zips(file_out_path, out_path) 
            files_to_textract.extend(unzipped_files)
        files_to_textract = [file_out_path] if len(files_to_textract) == 0 else files_to_textract
        for f in files_to_textract:
            filename = os.path.basename(f)
            text = textract_from_file(f, file_uri)
            machine_readable = True if text else False
            attachment_url = f'{file_uri}api_key={SAM_API_KEY}'
            attachment = {'filename': filename,
                          'machine_readable': machine_readable,
                          'attachment_text': text,
                          'attachment_url': attachment_url}
            attachments.append(attachment)
            os.remove(f)
           
    return attachments


def textract_from_file(file_out_path, file_uri):
    try:
        b_text = textract.process(file_out_path, encoding='utf-8', errors = 'ignore')
    except textract.exceptions.MissingFileError as e:
        b_text = None
        logger.error(f"Couldn't textract {file_out_path} from {file_uri} since the file couldn't be found:  \
                      {e}", exc_info=True)
    except (textract.exceptions.ExtensionNotSupported, TypeError, ModuleNotFoundError, zipfile.BadZipFile):
        # TypeError is raised when textract can't extract text from scanned documents
        # BadZipFile raised when a corrupt docx file is encountered
        # The others are raised when textract encounters an unsupported file extension (e.g. .ppt)
        b_text = None
    except Exception as e:
        file_name = os.path.basename(file_out_path)
        logger.error(f"Exception {e} occurred textracting {file_name} from {file_uri}", exc_info = True)
        b_text = None
    if b_text:
        text = b_text.decode('utf8', errors = 'ignore')
    else:
        text = ''
    text = text.strip()

    return text


def get_attachments(notices, out_path):
    for notice_type in notices:
        nt_notices = notices[notice_type]
        if not nt_notices:
            continue
        for notice in nt_notices:
            notice_id = os.path.basename(notice['url'])
            solicitation_number = notice['solnbr']
            attachment_data = attachments_get(notice_id, solicitation_number)
            if not attachment_data:
                notice['attachments'] = []
                continue
            attachments = textract_attachment(attachment_data, notice_id, out_path)
            notice['attachments'] = attachments

    return notices
