#!/usr/bin/env python3
import urllib.request
from contextlib import closing
import shutil
import re
import os
import json
import requests
from requests.exceptions import SSLError
from requests import exceptions
from bs4 import BeautifulSoup
from mimetypes import guess_extension
from .textract.textract import process
from .textract.textract.parsers.exceptions import ShellError
from zipfile import ZipFile, BadZipfile
import io
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

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
        
        try:
            r = requests.get(fbo_url)
        except Exception as e:
            logging.exception(f"Exception occurred getting attachment divs from {fbo_url}")
            attachment_divs = []
            return attachment_divs
        r_content = r.content
        soup = BeautifulSoup(r_content, "html.parser")
        attachment_divs = soup.find_all('div', {"class": "notice_attachment_ro"})
        
        return attachment_divs

    
    @staticmethod
    def get_attachment_text(file_name, url):
        '''
        Extract text from a file.

        Arguments:
            file (str): the path to a file.
            url  (str): the url of file (for logging purposes)

        Returns:
            text (str): a string representing the text of the file.
        '''
        try:
            b_text = process(file_name)
        except Exception as e:
            logging.exception(f"Exception occurred textracting from {url}")
            b_text = None
        if b_text:
            text = b_text.decode('utf-8', errors='ignore')
        else:
            text = ''
        text = text.strip()

        return text
    

    @staticmethod
    def insert_attachments(file_list, notice):
        '''
        Inserts each attachment's url and text into the nightly json file. Also inserts
        placeholders for the prediction, decision_boundary, and validation.

        Parameters:
            file_list (list): a list of tuples containing attachment file paths and urls
            notice (dict): a dict representing a single fbo notice

        Returns:
            notice (dict): a dict representing a single fbo notice with insertions made
        '''
        
        notice['attachments'] = []
        for file_url_tup in file_list:
            file_name, url = file_url_tup
            text = FboAttachments.get_attachment_text(file_name, url)
            attachment_dict = {'text':text, 
                               'url':url,
                               'prediction':None, 
                               'decision_boundary':None,
                               'validation':None,
                               'trained':False}
            notice['attachments'].append(attachment_dict)

        return notice

    
    @staticmethod
    def size_check(url):
        """
        Does the url contain a resource that's less than 500mb?

        Arguments:
            url (str): an attachment url that's passable `requests.head()`

        Returns:
            bool: True if resource < 500mb
        """
        try:
            h = requests.head(url)
        except Exception as e:
            logging.exception(f"Exception occurred getting file size with HEAD request from {url}")
            return False
        
        if h.status_code != 200:
            logging.warning(f'Non-200 status code getting file size with HEAD request from {url}')
            return False
        elif h.status_code == 302:
            header = h.headers
            redirect_url = header['Location']
            try:
                h = requests.head(redirect_url)
            except Exception as e:
                logging.exception(f"Exception occurred getting file size with redirected HEAD \
                                    request from {url}")
                return False
        header = h.headers
        content_length = header.get('content-length', None)
        if content_length and int(content_length) > 5e8:  # 500 mb approx
            return False
        else:
            return True
    

    @staticmethod
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
        file_name = file_name[0].strip('\"')
        
        return file_name

    
    @staticmethod
    def get_file_name(attachment_url, content_type):
            '''
            Get filename using some heuristics if get_filename_from_cd() failed.
            Arguments:
                attachment_url (str): the url for a fbo notice attachment
                content_type (str): the content-type as found in a requests response header

            Returns:
                file_name (str): a string for the file's name
            '''
            
            file_name = os.path.basename(attachment_url)
            extensions = ['.csv','.docx','.doc','.eml', '.epub', '.gif', '.html', '.jpeg', '.htm',
                          '.jpg', '.json', '.log', '.mp3', '.msg', '.odt', '.ogg', '.pdf', '.png', '.pptx',
                          '.ps', '.psv', '.rtf', '.tff', '.tiff', '.tsv', '.txt', '.wav', '.xlsx', '.xls']
            extensions_re = re.compile(r"|".join(extensions))
            matches = extensions_re.findall(file_name)
            if matches:
                for m in matches:
                    file_name = file_name.replace(m,'')
                extension = max(matches, key=len)
                file_name = file_name+extension
            else:
                if content_type == 'application/zip':
                    extension = '.zip'
                elif content_type == 'application/msword':
                    extension = '.rtf'
                else:
                    extension = guess_extension(content_type.split()[0].rstrip(";"))
                if not extension:
                    extension = '.txt'
                file_name = file_name + extension
            
            return file_name
    
    
    @staticmethod
    def get_neco_navy_mil_attachment_urls(attachment_href):
        '''
        Scrape the attachment urls from the https://www.neco.navy.mil/... page

        Arguments:
            attachment_href (str): the url, e.g. https://www.neco.navy.mil/.....

        Returns:
            attachment_urls (list): a list of the attachment urls scraped from the 
            dwnld2_row id of the html table
        '''

        try:
            r = requests.get(attachment_href)
        except Exception as e:
            logging.exception(f"Exception occurred getting attachment url from {attachment_href}")
            attachment_urls = []
            return attachment_urls
        r_content = r.content
        soup = BeautifulSoup(r_content, "html.parser")
        attachment_rows = soup.findAll("tr", {"id": "dwnld2_row"})
        attachment_urls = []
        for row in attachment_rows:
            file_path = row.find('a')['href']
            if 'https://www.neco.navy.mil' not in file_path:
                attachment_url = f'https://www.neco.navy.mil{file_path}'
            else:
                attachment_url = file_path
            attachment_urls.append(attachment_url)
        
        return attachment_urls


    @staticmethod
    def get_attachment_url_from_div(div):
        '''
        Extract the attachment url from the href attribute of the attachmen div's anchor tag

        Arguments:
            div (an element within the bs4 object returned by soup.find_all())

        Returns:
            attachment_url (str): the attachment's url as a string 
        '''
        attachment_href = div.find('a')['href'].strip()
        #some href's look like: 'http://  https://www....'
        attachment_href = max(attachment_href.split(), key=len)
        if '/utils/view?id' in attachment_href:
            attachment_url = 'https://www.fbo.gov'+attachment_href
        elif 'neco.navy.mil' in attachment_href:
            #this returns a list
            attachment_urls = FboAttachments.get_neco_navy_mil_attachment_urls(attachment_href)
            return attachment_urls
        else:
            attachment_url = attachment_href
        attachment_urls = [attachment_url]
        
        return attachment_urls
    
    
    @staticmethod
    def get_and_write_attachment_from_ftp(attachment_url, out_path, textract_extensions):
        '''
        Get and write a file from a FTP

        Arguments:
            attachment_url (str): the ftp url of the attachment
            out_path (str): the directory to which you'd like to write the attachment
            textract_extensions (tup): a tuple of file extensions

        Returns:
            file_out_path (str): the relative file path to which the ftp file was written
        '''

        file_name = os.path.basename(attachment_url)
        file_out_path = os.path.join(out_path, file_name)
        if file_out_path.endswith(textract_extensions):
            try:
                with closing(urllib.request.urlopen(attachment_url)) as ftp_r:
                    with open(file_out_path, 'wb') as f:
                        shutil.copyfileobj(ftp_r, f)
            except Exception as e:
                logging.exception(f"Exception occurred downloading FTP attachment from {attachment_url}")
                    
        return file_out_path

    @staticmethod
    def write_attachments(attachment_divs):
        '''
        Given a list of the attachment_divs from an fbo notice's url, write each file's contents
        and return a list of all of the files written.

        Parameters:
            attachment_divs (list): a list of attachment_divs. Returned by FboAttachments.get_divs()

        Returns:
            file_list (list): a list of tuples containing files paths and urls of each file that has been written
        '''

        textract_extensions = ('.doc', '.docx', '.epub', '.gif', '.htm', 
                               '.html','.odt', '.pdf', '.rtf', '.txt')
        out_path = 'attachments'
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        file_list = []
        for div in attachment_divs:
            try:
                attachment_urls = FboAttachments.get_attachment_url_from_div(div)
                for attachment_url in attachment_urls:
                    #some are ftp and we can get the file now
                    if 'ftp://' in attachment_url:
                        f = FboAttachments.get_and_write_attachment_from_ftp(attachment_url,
                                                                            out_path,
                                                                            textract_extensions)
                        file_list.append((f, attachment_url))                                                                                        
                    else:
                        if FboAttachments.size_check(attachment_url):
                            try:
                                r = requests.get(attachment_url, timeout=10)
                            except:
                                logging.exception(f"Exception occurred requesting attachment from {attachment_url}")
                                continue
                            if r.status_code == 302:
                                header = r.headers
                                redirect_url = header['Location']
                                try:
                                    r = requests.get(redirect_url)
                                except:
                                    logging.exception(f"Exception occurred requesting attachment from redirect {redirect_url}")
                                    continue
                            content_disposition = r.headers.get('Content-Disposition')
                            file_name = FboAttachments.get_filename_from_cd(content_disposition)
                            if not file_name:
                                content_type = r.headers.get('Content-Type')
                                file_name = FboAttachments.get_file_name(attachment_url, content_type)
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

        #clean up
        for file_url_tup in file_list:
            file_path, _ = file_url_tup
            os.remove(file_path)
        
        return updated_nightly_data

     