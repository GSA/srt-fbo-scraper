# -*- coding: utf-8 -*-

import urllib.request
from contextlib import closing
import shutil
import re
from collections import Counter
import os
from datetime import datetime
import json
import pandas as pd
import datetime
import requests
from requests import exceptions
from bs4 import BeautifulSoup
from mimetypes import guess_extension
import chardet
import textract
from textract.exceptions import ShellError
from zipfile import ZipFile, BadZipfile
import io


class FboAttachments():
    '''
    Given the json of a nightly fbo file, retrieve all of its attachments from the fbo url, 
    extract the text, and insert those details as new key:value pairs into the json.

    Parameters:
        nightly_data (json or dict): the json/dict representation of a nightly FBO file
    '''
    
    def __init__(self, nightly_data):
        self.nightly_data = nightly_data


    @staticmethod
    def get_divs(fbo_url):
        '''
        gets the `notice_attachment_ro` divs within given fbo url

        Parameters:
            fbo_url (str): a url to an fbo notice.

        Returns:
            attachment_divs (list): a list of each html div with its text
        '''
        
        r = requests.get(fbo_url)
        r_text = r.text
        soup = BeautifulSoup(r_text, "html.parser")
        attachment_divs = soup.find_all('div', {"class": "notice_attachment_ro"})
        return attachment_divs

    
    @staticmethod
    def insert_attachments(file_list, notice):
        '''
        Inserts each attachment's url and text into the nightly json file

        Parameters:
            file_list (list): a list of the attachment file paths that have been downloaded
            notice (dict): a dict representing a single fbo notice

        Returns:
            notice (dict): a dict representing a single fbo notice with insertions made
        '''
        
        def get_attachment_text(file):
            '''
            Extract text from a file.

            Arguments:
                file (str): the path to a file.

            Returns:
                text (str): a string representing the text of the file.
            '''
            try:
                b_text = textract.process(file)
            except BadZipfile:#this catches corruputed docx files
                b_text = None
            except ShellError:
                b_text = None
            if b_text:
                detected_encoding = chardet.detect(b_text)['encoding']
                if detected_encoding:
                    text = b_text.decode(detected_encoding, errors='ignore')
                else:
                    text = b_text.decode('utf-8', errors='ignore')
            else:
                text = ''

            return text
        
        notice['attachments'] = {}
        for i, tup in enumerate(file_list):
            file, url = tup
            text = get_attachment_text(file)
            temp_dict = {f'attachment{i+1}': {'text':text, "url":url}}
            notice['attachments'].update(temp_dict)

        return notice

    
    @staticmethod
    def write_attachments(attachment_divs):
        '''
        Given a list of the attachment_divs from an fbo notice's url, write each file's contents
        and return a list of all of the files written.

        Parameters:
            attachment_divs (list): a list of attachment_divs. Returned by FboAttachments.get_divs()

        Returns:
            file_list (list): a list of all the files that have been written
        '''
        
        def size_check(url):
            """
            Does the url contain a resource that's less than 500mb?

            Arguments:
                url (str): an attachment url that's passable `requests.head()`

            Returns:
                bool: True if resource < 500mb
            """
            h = requests.head(url)
            header = h.headers
            content_length = header.get('content-length', None)
            if content_length and int(content_length) > 5e8:  # 500 mb approx
                return False
            else:
                return True
        
        def get_filename_from_cd(cd):
            """
            Get filename from content-disposition

            Arguments:
                cd: the content-disposition returned in the headers by requests.get()

            Returns:
                file_name (str) or None
            """
            
            if not cd:
                return None
            file_name = re.findall('filename=(.+)', cd)
            if len(file_name) == 0:
                return None
            file_name = file_name[0]
            return file_name
        
        def get_file_name(attachment_url, content_type):
            '''
            Get filename using some heuristics if get_filename_from_cd() failed.
            Arguments:
                attachment_url (str): the url for a fbo notice attachment
                content_type (str): the content-type as found in a requests response header

            Returns:
                file_name (str): a string for the file's name
            '''
            
            file = os.path.basename(attachment_url)
            extensions = ['.csv','.docx','.doc','.eml', '.epub', '.gif', '.html', '.jpeg', '.htm',
                          '.jpg', '.json', '.log', '.mp3', '.msg', '.odt', '.ogg', '.pdf', '.png', '.pptx',
                          '.ps', '.psv', '.rtf', '.tff', '.tiff', '.tsv', '.txt', '.wav', '.xlsx', '.xls']
            extensions_re = re.compile(r"|".join(extensions))
            matches = extensions_re.findall(file)
            if matches:
                for m in matches:
                    file = file.replace(m,'')
                extension = max(matches, key=len)
                file_name = file+extension
            else:
                if content_type == 'application/zip':
                    extension = '.zip'
                elif content_type == 'application/msword':
                    extension = '.rtf'
                else:
                    extension = guess_extension(content_type.split()[0].rstrip(";"))
                if not extension:
                    extension = '.txt'
                file_name = file + extension
            return file_name

        textract_extensions = ('.csv', '.doc', '.docx', '.eml', '.epub', '.gif', '.htm', 
                               '.html', '.jpeg', '.jpg', '.json', '.log', '.mp3', '.msg',
                               '.odt', '.ogg', '.pdf', '.png', '.pptx', '.ps', '.psv',
                               '.rtf', '.tff', '.tif', '.tiff', '.tsv', '.txt', '.wav',
                               '.xls', '.xlsx')
        out_path = 'attachments'
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        file_list = []
        for d in attachment_divs:
            try:
                attachment_href = d.find('a')['href'].strip()
                if '/utils/view?id' in attachment_href:
                    attachment_url = 'https://fbo.gov'+attachment_href
                #some href's look like: 'http://  https://www....'
                elif ' ' in attachment_href:
                    attachment_url = max(attachment_href.split(), key=len)
                else:
                    attachment_url = attachment_href
                #some are ftp
                if 'ftp://' in attachment_url:
                    file_name = os.path.basename(attachment_url)
                    file_out_path = os.path.join(out_path, file_name)
                    if file_out_path.endswith(textract_extensions):
                        with closing(urllib.request.urlopen(attachment_url)) as ftp_r:
                            with open(file_out_path, 'wb') as f:
                                shutil.copyfileobj(ftp_r, f)
                        file_list.append((file_out_path, attachment_url))
                else:
                    if size_check(attachment_url):
                        r = requests.get(attachment_url, timeout=10)
                        content_disposition = r.headers.get('Content-Disposition')
                        file_name = get_filename_from_cd(content_disposition)
                        if not file_name:
                            content_type = r.headers.get('Content-Type')
                            file_name = get_file_name(attachment_url, content_type)
                        if '.zip' in file_name:
                            z = ZipFile(io.BytesIO(r.content))
                            z.extractall(out_path)
                            zip_file_list = z.filelist
                            for zip_file in zip_file_list:
                                file_out_path = os.path.join(out_path,zip_file)
                                if file_out_path.endswith(textract_extensions):
                                    file_list.append((file_out_path, attachment_url))
                        else:
                            file_out_path = os.path.join(out_path,file_name).replace('"','')
                            if file_out_path.endswith(textract_extensions):
                                with open(file_out_path, 'wb') as f:
                                    f.write(r.content)
                                file_list.append((file_out_path, attachment_url))
                    else:
                        pass
            except:
                continue
        return file_list
    
    def update_nightly_data(self):
        '''
        Given the json of a nightly fbo file, retrieve all of its attachments from the fbo url, 
        extract the text, and insert those details as new key:value pair(s) into the json.

        Returns:
            updated_nightly_data (dict): a dict representing a nightly file with attachment urls
            and attachment text inserted as new key:value pairs.
        '''
        
        nightly_data = self.nightly_data
        for k in nightly_data:
            for i, notice in enumerate(nightly_data[k]):
                try:
                    fbo_url = notice['url']
                except:
                    continue
                attachment_divs = FboAttachments.get_divs(fbo_url)
                file_list = FboAttachments.write_attachments(attachment_divs)
                updated_notice = FboAttachments.insert_attachments(file_list, notice)
                nightly_data[k][i] = updated_notice
        updated_nightly_data = nightly_data
        return updated_nightly_data

     