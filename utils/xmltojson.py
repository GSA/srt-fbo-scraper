import json

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


def elem_to_json(elem, strip=True):
  """Convert an Element into a JSON string.
  Arguments:
      elem (object):  an xml.etree.ElementTree.Element
      strip (bool):  whether or not to ignore leading and trailing whitespace
                     in the text that maps to the xml tags
  Returns:
      json_string (str): a str representing JSON
  """

  if hasattr(elem, 'getroot'):
      elem = elem.getroot()
  json_string = json.dumps(elem_to_dict(elem,strip=strip))
  return json_string
