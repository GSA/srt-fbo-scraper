import urllib.request
from contextlib import closing
import shutil
import re
from collections import Counter
import os
from datetime import datetime
import json
import pandas as pd


class NightlyFBONotices():
    '''
    Download nightly FBO file, converting pseudo-xml into JSON.

    Attributes:
        date (str): The date of the nightly file to download. Format:  YYYYMMDD
                    (e.g. '20180506')
        base_url (str): the base url for the FBO FTP. By default it is set to:
                        ftp://ftp.fbo.gov/FBOFeed
    '''

    def __init__(self, date, base_url='ftp://ftp.fbo.gov/FBOFeed'):
        self.base_url = base_url
        self.date = str(date)
        self.ftp_url = base_url+self.date
        


    @staticmethod
    def id_and_count_notice_tags(file_lines):
        '''
        Static method to count the number of notice tags within a FBO export.

        Attributes:
            file_lines (list): A list of lines from the nightly FBO file.

        Returns:
            tag_count (dict): An instance of a collections.Counter object
                               containing tags as keys and their counts as
                               values
        '''

        end_tag = re.compile(r'\</[A-Z]*>')
        alphas_re = re.compile('[^a-zA-Z]')
        tags = []   # instantiate empty list
        for line in file_lines:
            try:
                match = end_tag.search(line)
                m = match.group()
                tags.append(m)
            except AttributeError:
                pass#these are all of the non record-type tags
        clean_tags = [alphas_re.sub('', x) for x in tags]
        tag_count = Counter(clean_tags)

        return tag_count


    @staticmethod
    def merge_dicts(dicts):
        d = {}
        for dict in dicts:
            for key in dict:
                try:
                    d[key].append(dict[key])
                except KeyError:
                    d[key] = [dict[key]]
        return {k:" ".join(v) for k, v in d.items()}


    def get_and_write_file(self):
        '''
        Downloads and writes a nightly FBO file.

        Returns:
            file_name (str): the absolute path to the downloaded file.
        '''

        file_name = 'fbo_nightly_'+self.date
        out_path = os.path.join(os.getcwd(),"temp/nightly_files")
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        with closing(urllib.request.urlopen(self.ftp_url)) as r:
            file_name = os.path.join(out_path,file_name)
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(r, f)

        return file_name


    def pseudo_xml_to_json(self, file_name):
        '''
        Open nightly file and convert the pseudo-xml to JSON

        Arguments:
            file_name (str): the absolute path to the downloaded file

        Returns:
            json_str (str): a string representing the JSON
        '''

        with open(file_name,'r',errors='ignore') as f:
            file_lines = f.readlines()
        with open(r'utils/html_tags.txt','r') as f:
            html_tags = f.read().splitlines()
        html_tag_re = re.compile(r'|'.join('(?:</?{0}>)'.format(x) for x in html_tags))
        alphas_re = re.compile('[^a-zA-Z]')
        notice_types = {'PRESOL','SRCSGT','SNOTE','SSALE','COMBINE','AMDCSS',
                        'MOD','AWARD','JA','FAIROPP','ARCHIVE','UNARCHIVE',
                        'ITB','FSTD','EPSUPLOAD','DELETE'}
        notice_type_start_tag_re = re.compile(r'|'.join('(?:<{0}>)'.\
                                               format(x) for x in notice_types))
        notice_type_end_tag_re = re.compile(r'|'.join('(?:</{0}>)'.\
                                               format(x) for x in notice_types))
        # returns two groups, the sub-tag as well as the text corresponding to it
        sub_tag_groups = re.compile(r'\<([a-z]*)\>(.*)')

        notices_dict_incrementer = {k:0 for k in notice_types}
        tag_count = NightlyFBONotices.id_and_count_notice_tags(file_lines)
        matches_dict = {k:{k:[] for k in range(v)} for k,v in tag_count.items()}
        # Loop through each line searching for start-tags, then end-tags, then
        # sub-tags (after stripping html) and then ensuring that every line of
        # multi-line tag values is captured.
        last_clean_notice_start_tag = ''
        last_sub_tab = ''
        for line in file_lines:
            try:
                match = notice_type_start_tag_re.search(line)
                m = match.group()
                clean_notice_start_tag = alphas_re.sub('', m)
                last_clean_notice_start_tag = clean_notice_start_tag
            except AttributeError:
                try:
                    match = notice_type_end_tag_re.search(line)
                    m = match.group()
                    #clean_notice_end_tag = alphas_re.sub('', m).strip()
                    notices_dict_incrementer[last_clean_notice_start_tag] += 1
                    continue #continue since we found an ending notice tag
                except AttributeError:
                    line_lower = line.lower().replace(u'\xa0', u' ')
                    line_lower_htmless = ' '.join(html_tag_re.sub(' ',line_lower).split())
                    try:
                        matches = sub_tag_groups.search(line_lower_htmless)
                        groups  = matches.groups()
                        sub_tag = groups[0]
                        last_sub_tab = sub_tag
                        sub_tag_text = groups[1]
                        current_tag_index = notices_dict_incrementer[last_clean_notice_start_tag]
                        matches_dict[last_clean_notice_start_tag][current_tag_index].append({sub_tag:sub_tag_text})
                    except AttributeError:
                        record_index = 0
                        for i,record in enumerate(matches_dict[last_clean_notice_start_tag][current_tag_index]):
                            if last_sub_tab in record:
                                record_index = i
                        matches_dict[last_clean_notice_start_tag][current_tag_index][record_index][last_sub_tab] += " " + line_lower_htmless
        notices_dict = {k:None for k in notice_types}
        for k in matches_dict:
            dict_list = [v for k,v in matches_dict[k].items()]
            notices_dict[k] = dict_list

        merge_notices_dict = {k:[] for k in notices_dict}
        for k in notices_dict:
            notices = notices_dict[k]
            if notices:
                for notice in notices:
                    merged_dict = NightlyFBONotices.merge_dicts(notice)
                    merge_notices_dict[k].append(merged_dict)
            else:
                pass

        json_str = json.dumps(merge_notices_dict)

        return json_str

    def write_json(self, json_string, file_name):
        '''
        Void function that writes a json string to disk.
        Arguments:
            json_strin (str): a string of json
            file_name (str): the name of the json file to write to.

        '''
        if '.json' not in file_name:
            file_name += '.json'
        out_path = os.path.join(os.getcwd(),"temp","nightly_files")
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        json_file_path = os.path.join(out_path, file_name)
        with open(json_file_path, 'w') as f:
            json.dump(json_string, f)


if __name__ == '__main__':
    #sample usage
    date=20180506
    nfbo = NightlyFBONotices(date=date)
    file_name = nfbo.get_and_write_file()
    json_str = nfbo.pseudo_xml_to_json(file_name)
    file_name = 'fbo_nightly_'+str(date)+'.json'
    nfbo.write_json(json_str,file_name)
