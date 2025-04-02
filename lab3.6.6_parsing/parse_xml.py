import xml.etree.ElementTree as ET

xml_data = '''<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target><candidate/></target>
    <default-operation>merge</default-operation>
    <test-option>set</test-option>
    <config>
      <int8.1 xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
              nc:operation="create"
              xmlns="http://netconfcentral.org/ns/test">9</int8.1>
    </config>
  </edit-config>
</rpc>'''

root = ET.fromstring(xml_data)
ns = {
    'nc': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'default': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'test': 'http://netconfcentral.org/ns/test'
}


message_id = root.attrib['message-id']
default_op = root.find('.//default:default-operation', ns).text
test_option = root.find('.//default:test-option', ns).text
int8_value = root.find('.//test:int8.1', ns).text


print(f"Message ID: {message_id}")
print(f"Default Operation: {default_op}")
print(f"Test Option: {test_option}")
print(f"int8.1 Value: {int8_value}")