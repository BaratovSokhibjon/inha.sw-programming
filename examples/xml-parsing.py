from src import parse_xml

with open("data/myfile_12225259.xml", "r") as file:
    xml_string = file.read()
    parsed_data = parse_xml.parse_xml(xml_string)

print(f"Default operation: {parsed_data['default-operation']}")
print(f"Test option: {parsed_data['test-option']}")