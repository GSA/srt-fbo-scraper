# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import urllib.request
from contextlib import closing
import shutil
import os
from mimetypes import guess_extension
import chardet
from requests import exceptions
import textract

 
def append_attachments(json_data):
    for k in json_data:
        for notice in json_data[k]:
            try:
                fbo_url = notice['url']
            except:
                continue
            print(fbo_url)
            attachment_divs = _get_attachment_divs(fbo_url)
            _append_attachments(attachment_divs,notice)

    
def _write_file(attachment_url, file_name, out_path):
    '''
    Void function that, given a url to an attachment, downloads and writes it.
    
    Arguments:
        attachment_url (str): the url of the document
        file_name (str): what you'd like to save that document as
        out_path (str): where you'd like to save that document
        
    Returns:
        None
    '''

    r = requests.get(attachment_url, timeout=10)
    if '/utils/view?id' in attachment_url:
        content_type = r.headers['Content-Type']
        if content_type == 'application/msword':
            extension = '.rtf'
        else:
            extension = guess_extension(content_type.split()[0].rstrip(";"))
        # no extensions found for 'application/vnd.openxmlformats-o' content-type
        if not extension:
            extension = '.docx'
        file_name = os.path.join(out_path, file_name+extension)
    elif 'ftp://' in attachment_url:
        with closing(urllib.request.urlopen(attachment_url)) as r:
            file_name = os.path.join(out_path, file_name)
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(r, f)
    else:
        file_name = os.path.join(out_path, file_name)
    with open(file_name, mode='wb') as f:
        f.write(r.content)





def _get_attachment_divs(fbo_url):
    '''
    gets the divs for each url 
    '''
    r = requests.get(fbo_url)
    r_text = r.text
    soup = BeautifulSoup(r_text, "html.parser")
    attachment_divs = soup.find_all('div', {"class": "notice_attachment_ro"})
    return attachment_divs



def _append_attachments(attachment_divs,notice):
    '''
    Appends each attachment into the nightly json file
    '''
    notice['attachments'] = {}
    count = 1
    for i,d in enumerate(attachment_divs):
            try:
                attachment_href = d.find('a')['href']
                if '/utils/view?id' in attachment_href:
                    attachment_url = 'https://fbo.gov'+attachment_href
                else:
                    attachment_url = attachment_href
                _saveAttachment(attachment_url)
                text = _get_attachment_text("attachments")
                tempDict = {'attachment%s' % count: {'text':text,"url":attachment_url}}
                notice['attachments'].update(tempDict)
                count +=1
            except:
                continue
    

def _saveAttachment(attachment_url):
    '''
    Saves each attachment as a temp file
    '''
    file_name = os.path.basename("tempFile")
    out_path = os.path.join(os.getcwd(),"attachments")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    try:
        _write_file(attachment_url, file_name, out_path)
    except exceptions.Timeout:
        print(f"Connection timed out after 10 seconds.\n\t Perhaps inspect:  {attachment_url}")
    except Exception as e:
        print(f"Failed:  {e}.\n\t Perhaps inspect:  {attachment_url}")



def _get_attachment_text(attachments_path):
    '''
    Void function that extracts and writes to a new dir the text from all the files in `attachments_path`.
    
    Arguments:
        attachments_path(str): the directory name where the FBO attachments are located.
        
    Returns:
        None
    '''
    
    out_path = 'attachments'
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for file in os.listdir(attachments_path):
        if file.startswith('.'):
            continue
        else:
            file_path = os.path.join(attachments_path,file)
            try:
                b_text = textract.process(file_path, encoding='utf-8')
                detected_encoding = chardet.detect(b_text)['encoding']
                text = b_text.decode(detected_encoding)
                base = os.path.splitext(file)[0]
                out_file = base+'.txt'
                out = os.path.join(out_path, out_file)
                with open(out, 'w') as f:
                    f.write(text)
            except Exception as e:
                print("-"*80)
                print(e)
                print(file)
                text =""
            if os.path.exists(file):
                os.remove(file)
            if os.path.exists(out_file):
                os.remove(out_file)
    return(text)
     




