import argparse
from datetime import timedelta, datetime
import json
import logging
import os

from utils.get_attachments import get_attachments
from utils.get_notices import get_notices

parser = argparse.ArgumentParser(description = ('Get ICT solictations from beta.sam.gov between two dates inclusive '
                                                '(if both flags are used) or from the day before yesteday.'))
parser.add_argument('--start-date',
                    dest = 'start_date',
                    type = str,
                    help = "the first date in the range you'd like to fetch notices from. Supply as a string ('%%Y-%%m-%%d')")
parser.add_argument('--end-date',
                    dest = 'end_date',
                    type = str,
                    help = "the last date in the range you'd like to fetch notices from. Supply as a string ('%%Y-%%m-%%d')")
logger = logging.getLogger(__name__)

def get_dates(start_date = None, end_date = None):
    """Return a list of dates between start_date and end_date inclusive if params provided; else return a list
    with just the date from two days ago.
    
    Keyword Arguments:
        start_date {[str]} -- [date "%Y-%m-%d"] (default: None)
        end_date {[str]} -- [date "%Y-%m-%d"] (default: None)
    
    Returns:
        [list] -- [list of date strings]
    """
    
    fbo_dates = []
    if all([start_date, end_date]):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        delta = end_date - start_date
        for i in range(delta.days + 1):
            fbo_date = start_date + timedelta(i)
            fbo_date = fbo_date.strftime("%Y-%m-%d")
            fbo_dates.append(fbo_date)
    else:
        now_minus_three = datetime.utcnow() - timedelta(3)
        now_minus_three = now_minus_three.strftime("%Y-%m-%d")
        fbo_dates.append(now_minus_three)
    
    return fbo_dates

def make_attachment_outpath():
    """Make a temporary directory in the root of the project for the downloaded attachments.
    
    Returns:
        [str] -- [absolute path to the created directory]
    """
    cwd = os.getcwd()
    if 'fbo-scraper' in cwd:
        i = cwd.find('fbo-scraper')
        root_path = cwd[:i+len('fbo-scraper')]
    else:
        i = cwd.find('root')
        root_path = cwd
    attachments_dir = 'attachments'
    out_path = os.path.join(root_path, attachments_dir) 
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    return out_path    

def main():
    args = parser.parse_args()
    fbo_dates = get_dates(start_date = args.start_date,
                          end_date = args.end_date)
    out_path = make_attachment_outpath()
    all_notices = []
    for d in fbo_dates:
        notices = get_notices(modified_date = d)
        if not notices:
            #no matching notices found for the day
            continue
        notices = get_attachments(notices, out_path)
        all_notices.append(notices)
        #TODO database insert here
    
    return all_notices
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    all_notices = main()
    with open('sam_results.json', 'w') as f:
        json.dump(all_notices, f)
