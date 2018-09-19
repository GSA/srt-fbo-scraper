import json
import urllib.request
from contextlib import closing
import shutil
import datetime
import os
import xml.etree.ElementTree as ET



def write_weekly_file(url):
    '''Given the FBO FTP weekly url, download and write the xml.
    Arguments
        url (str):  the FTP url for the weekly data. Should be
                    'ftp://ftp.fbo.gov/datagov/FBOFullXML.xml'
    Returns:
        file_path (str): the abs path of the xml file
    '''


    out_path = os.path.join(os.getcwd(),"weekly_files")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    now = datetime.datetime.now().strftime('%m-%d-%y')
    file_name = 'fbo_weekly_'+now+'.xml'
    with closing(urllib.request.urlopen(url)) as r:
        file_path = os.path.join(out_path, file_name)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r, f)
    return file_path


def elem_to_dict(elem,strip=True):
    """Recursive function that converts an xml.etree.ElementTree.Element into a dictionary.
    Arugments:
        elem (an xml.etree.ElementTree.Element instance):  after creating an ElemenTree object from an xml file,
                                                           the getroot() method will return an Element object.
        strip (bool): whether or not to ignore leading and trailing whitespace in the text that corresponds to
                      the xml tags.

    Returns:
        tag_dict (dict): a dict containing and Element tag name and the text that corresponds to it.
    """

    d = {}
    for key, value in elem.attrib.items():
        d['@'+key] = value
    # loop over subelements to merge them
    for subelem in elem:
        v = elem_to_dict(subelem,strip=strip)
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

def elem2json(elem, strip=True):
    """Convert an ElementTree or Element into a JSON string.
    """

    if hasattr(elem, 'getroot'):
        elem = elem.getroot()
    return json.dumps(elem_to_dict(elem,strip=strip))


if __name__ == "__main__":
    url = 'ftp://ftp.fbo.gov/datagov/FBOFullXML.xml'
    # This takes a few minutes (roughly 1.7GB to write)
    file_path = write_weekly_file(url)
    # Create an ElementTree object from the xml
    tree = ET.parse(file_path)
    # As an Element, root has a tag and a dictionary of attributes
    root = tree.getroot()
    # Create JSON string from root (an Element object)
    elem_json = elem2json(root)
    # Write the json
    json_file_path = file_path.replace("xml","json")
    with open(json_file_path, 'w') as f:
        json.dump(elem_json, f)
