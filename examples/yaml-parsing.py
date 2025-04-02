from src import parse_yaml
with open('data/myfile_12225259.yaml', 'r') as file:
    yaml_string = file.read()
    parsed_data = parse_yaml.parse_yaml(yaml_string)

print("The access token is {}".format(parsed_data['access_token']))
print("The token expires in {} seconds.".format(parsed_data['expires_in']))