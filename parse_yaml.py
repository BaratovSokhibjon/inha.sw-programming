import yaml

with open('myfile_12235649.yaml', 'r') as file:
    parsed_data = yaml.safe_load(file) 

print("The access token is {}".format(parsed_data['access_token']))
print("The token expires in {} seconds.".format(parsed_data['expires_in']))
print("The refresh token is {}".format(parsed_data['refresh_token']))
print("The refresh token expires in {} seconds.".format(parsed_data['refreshtokenexpires_in']))