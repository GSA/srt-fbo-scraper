import urllib
from contextlib import closing
import shutil
import pandas as pd
import re
from collections import Counter
import numpy as np
import os
from datetime import datetime
from functools import reduce

delimiter = re.compile(r'\<([A-Z]*)\>(.*)')
section_end = re.compile(r'\</[A-Z]*\>')

def get_and_write_file(url):
    num_re = re.compile(r'[\d]+')
    match = num_re.search(url)
    date = match.group()
    file_name = 'fbo_'+date

    out_path = os.path.join(os.getcwd(),"raw_fbo_pbs_files")
    if not os.path.exists(out_path):
        os.makedirs(out_path)


    with closing(urllib.request.urlopen(url)) as r:
        file = os.path.join(out_path,file_name)
        with open(file, 'wb') as f:
            shutil.copyfileobj(r, f)
    return file

def open_file(file_name,remove_file=False):
    with open(file_name, mode = 'r', encoding = 'Latin1') as f:
        lines = f.readlines()
    if remove_file:
        os.remove(file_name)
    return lines

def id_and_count_meta_tags(lines, desired_tags):
    end_tag = re.compile(r'\</[A-Z]*>')
    alphas_re = re.compile('[^a-zA-Z]')
    tags = []   # instantiate empty list
    for line in lines:
        try:
            match = end_tag.search(line)
            m = match.group()
            tags.append(m)
        except AttributeError:
            pass#these are all of the non record-type tags
    clean_tags = [alphas_re.sub('', x) for x in tags]
    tag_counts = Counter(clean_tags)

    return tag_counts


def parse_lines(lines, tag_counts, desired_tags):
    with open('html_tags.txt','r') as f:
        html_tags = set([tag.strip() for tag in f.readlines()])
        html_tag_replacement_map = {k:'' for k in html_tags}

    # create a dict with keys for each meta-tag and then sub-dicts for each record
    # (e.g. <PRESOL> might have 200 records within the file and therefore
    # 200 sub-dicts). The sub-dicts will have ints as keys representing their
    # index and empty lists initialized for values.
    matches_dict = {k:{k : [] for k in range(v)} for k,v in tag_counts.items()}

    #instantiate a counter at -1
    match_dict_index = -1

    #this list will be populated with tags once I've parsed through them
    spent_tags = []

    for line in lines:
        #strip html tags and whitespace from line
        l = reduce(lambda a, kv: a.replace(*kv), html_tag_replacement_map.items(), line).strip()
        if l in desired_tags:
            t = l.replace("<","").replace(">","")
            spent_tags.append(t)

            # test to see if the tag that was just appended is in the spent_tags list more than once.
            # If so, increment
            if len(spent_tags) > 1 and spent_tags.count(t) > 1:
                match_dict_index  += 1
            #else set the counter to 0
            else:
                match_dict_index = 0
                continue

        try:
            match = delimiter.search(l)
            #first element of match is tag; second is text that follows that tag
            if match:
                m = list(match.groups()) #convert to list since tuples are immutable
                #if this is present the <DESC> sub tag is duplicated
                if m == ['DESC', 'Link To Document']:
                    pass
                else:
                    matches_dict[t][match_dict_index].append(m)
            else:
                pass
        # if it hasn't been assigned (meaning none of the desired tags are in the FBO file)
        except UnboundLocalError:
            pass
        #if the delimiter isn't in the line...
        except AttributeError:
            #skip line if the line is blank or is the end of a section
            if len(l.rstrip()) == 0 or section_end.search(l):
                pass
            #for all other lines, append the line to the previously found match
            else:
                last_spot = matches_dict[t][match_dict_index]
                matches_dict[t][match_dict_index][len(last_spot)-1][1] += " " + l

    return matches_dict

def create_data_frames(parsed_dict, date):
    data_dict = dict.fromkeys(parsed_dict.keys())
    date = datetime.strptime(date, '%Y%m%d').strftime('%m/%d/%Y')

    for tag in parsed_dict:
        l = []
        for i in parsed_dict[tag]:
            d = {}
            l.append(d)
            for k in parsed_dict[tag][i]:
                k_dict = dict([k])
                d.update(k_dict)
        data_dict[tag] = l

    dfs_dict = dict.fromkeys(parsed_dict.keys())
    for k in data_dict:
        df = pd.DataFrame(data_dict[k])
        df['FBO File Date'] = date
        df.name = k + "_" + date
        dfs_dict[k] = df

    return dfs_dict

# run the script with dummy data
dates = {'20180506','20180507','20180508','20180509','20180510'}
report_types = {'PRESOL','SRCSGT','SNOTE','SSALE','COMBINE','AMDCSS','MOD','AWARD',
                'JA','FAIROPP','ARCHIVE','UNARCHIVE'}
desired_tags = set(["<"+x+">" for x in report_types])

dfs = []
for date in dates:
    url = r'ftp://ftp.fbo.gov/FBOFeed'+date
    file_name = get_and_write_file(url)
    lines = open_file(file_name)
    tag_counts = id_and_count_meta_tags(lines, desired_tags)
    matches_dict = parse_lines(lines, tag_counts, desired_tags)
    dfs_dict = create_data_frames(matches_dict, date)
    dfs.append(dfs_dict)

desired_reports = {k:[] for k in report_types}
for d in dfs:
    for k in d:
        if k in report_types:
            desired_reports[k].append(d[k])

final = {k:None for k in report_types}
for k in desired_reports:
    data = pd.concat(desired_reports[k],sort=True)
    final[k] = (data)
    # make a file path for the data that will be written

out_path = os.path.join(os.getcwd(),"data_files")
if not os.path.exists(out_path):
    os.makedirs(out_path)

#delete any files that are already in the out_path
for the_file in os.listdir(out_path):
    file_path = os.path.join(out_path, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(e)

out_file = os.path.join(out_path,'FBO Report.xlsx')
writer = pd.ExcelWriter(out_file)
for k in final:
    d = final[k]
    d.to_excel(writer,k,index=False)

writer.save()
