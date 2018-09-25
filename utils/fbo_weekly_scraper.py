import json
import urllib.request
from contextlib import closing
import shutil
import datetime
import os
import xml.etree.ElementTree as ET
import pandas as pd

class FBONotices():
    '''

    '''

    def __init__(self):
        pass


    def write_xml(self):
        '''Download and write the weekly FBO xml file.
        Returns:
            xml_file_path (str): abs path to the xml just downloaded.
        '''

        url = 'ftp://ftp.fbo.gov/datagov/FBOFullXML.xml'
        out_path = os.path.join(os.getcwd(),"weekly_files")
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        now = datetime.datetime.now().strftime('%m-%d-%y')
        file_name = 'fbo_weekly_'+now+'.xml'
        with closing(urllib.request.urlopen(url)) as r:
            xml_file_path = os.path.join(out_path, file_name)
            with open(xml_file_path, 'wb') as f:
                shutil.copyfileobj(r, f)
        return xml_file_path


    @staticmethod
    def elem_to_dict(elem,strip=True):
        """Recursive function that converts an xml.etree.ElementTree.Element
        into a dictionary.
        Arguments:
            elem (object): after creating an ElemenTree object
                                        from an xml file, the getroot() method
                                        will return an Element object.
            strip (bool): whether or not to ignore leading and trailing
                          whitespace in the text that maps to the xml tags.
        Returns:
            tag_dict (dict): a dict containing and Element tag name and the
                            text that corresponds to it.
        """

        d = {}
        for key, value in elem.attrib.items():
            d['@'+key] = value
        # loop over subelements to merge them
        for subelem in elem:
            v = FBONotices.elem_to_dict(subelem,strip=strip)
            tag = subelem.tag
            value = v[tag]
            try:
                # add to existing list for this tag
                d[tag].append(value)
            except AttributeError:
                # turn existing entry into a list
                d[tag] = [d[tag], value]
            except KeyError:
                # add a new non-list entry
                d[tag] = value
        text = elem.text
        tail = elem.tail
        if strip:
            # ignore leading and trailing whitespace
            if text:
                text = text.strip()
            if tail:
                tail = tail.strip()
        if tail:
            d['#tail'] = tail
        if d:
            # use #text element if other attributes exist
            if text:
                d["#text"] = text
        else:
            # text is the value if no attributes
            d = text or None
        tag_dict = {elem.tag: d}
        return tag_dict


    @staticmethod
    def elem_to_json(elem, strip=True):
        """Convert an Element into a JSON string.
        Arguments:
            elem (object):  an xml.etree.ElementTree.Element
        Returns:
            json_string (str): a str representing JSON
        """

        if hasattr(elem, 'getroot'):
            elem = elem.getroot()
        json_string = json.dumps(FBONotices.elem_to_dict(elem,strip=strip))
        return json_string


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
        json_string = FBONotices.elem_to_json(root)
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
