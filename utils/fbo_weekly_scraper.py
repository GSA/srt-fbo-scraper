#!/usr/bin/env python3
import json
import urllib.request
from contextlib import closing
import shutil
import datetime
import os
import xml.etree.ElementTree as ET
import pandas as pd
import xmltojson

class FBONotices():
    '''
    Provides an interface to the FBO FTP, providng methods to download the xml,
    conver it to json, write that json, and convert that json to pandas
    dataframes.

    Atributes:
        ftp_ulr:  the FTP url for the weekly FBO files. These files are updated
                  weekly betwee 2-3am Sunday mornings.

    '''

    def __init__(self,ftp_url='ftp://ftp.fbo.gov/datagov/FBOFullXML.xml'):
        self.ftp_url = ftp_url


    def write_xml(self):
        '''Download and write the weekly FBO xml file.
        Returns:
            xml_file_path (str): abs path to the xml just downloaded.
        '''

        out_path = os.path.join(os.getcwd(),"weekly_files")
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        now = datetime.datetime.now().strftime('%m-%d-%y')
        file_name = 'fbo_weekly_'+now+'.xml'
        with closing(urllib.request.urlopen(self.ftp_url)) as r:
            xml_file_path = os.path.join(out_path, file_name)
            with open(xml_file_path, 'wb') as f:
                shutil.copyfileobj(r, f)
        return xml_file_path


    def xml_to_json(self,xml_file_path):
        '''Convert an xml file into a json string
        Arguments:
            file (str): xml file name
        Returns:
            elem_json (str): a str of json
        '''

        # Create an ElementTree object from the xml file
        tree = ET.parse(xml_file_path)
        # As an Element, root has a tag and a dictionary of attributes
        root = tree.getroot()
        json_string = xmltojson.elem_to_json(root)
        return json_string


    def write_json(self, json_string, file_name):
        '''Writes a json string to disk.
        Arguments:
            json_strin (str): a string of json
            file_name (str): the name of the json file to write to.

        '''
        if '.json' not in file_name:
            file_name += '.json'
        out_path = os.path.join(os.getcwd(),"weekly_files")
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        json_file_path = os.path.join(out_path, file_name)
        with open(json_file_path, 'w') as f:
            json.dump(json_string, f)

    def json_to_dfs(self, json_string, notice_type=None):
        fbo_json = json.loads(json_string)
        # get the json object for the Notices key
        notices_dict = fbo_json['NOTICES']
        # instantiate a dict with keys for each notice type
        df_dict = {k:None for k in notices_dict}
        # create a dictionary of dataframes
        for k in notices_dict:
            df_dict[k] = pd.DataFrame.from_dict(notices_dict[k])
        # TODO: create dfs only for desired notice types
        return df_dict


if __name__ == "__main__":
    fbo = FBONotices()
    # This takes a few minutes (roughly 1.7GB to write and then convert to json)
    xml_file_path = fbo.write_xml()
    json_string = fbo.xml_to_json(xml_file_path)
    now = datetime.datetime.now().strftime('%m-%d-%y')
    file_name = 'fbo_weekly_'+now+'.json'
    fbo.write_json(json_string, file_name)
