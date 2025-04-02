import xml.etree.ElementTree as ET
import re

def parse_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
        ns = re.match('{.*}', root.tag).group(0)

        editconf = root.find("{}edit-config".format(ns))
        defop = editconf.find("{}default-operation".format(ns))
        testop = editconf.find("{}test-option".format(ns))
        
        return {
            "default-operation": defop.text,
            "test-option": testop.text
        }
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None