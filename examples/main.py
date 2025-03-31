from src import parse_json

with open("data/myfile_12225259.json", "r") as file:
    json_string = file.read()
    parsed_data = parse_json.parse_json(json_string)

print(f"Access token: {parsed_data['access_token']}")
print(f"Expires in seconds: {parsed_data['expires_in']}")