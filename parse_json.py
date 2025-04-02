import json

try:
    with open('myfile_12235649.json') as f:
        data = json.load(f)
    print(f"Access token: {data['access_token']}\nExpires in: {data['expires_in']} sec")
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"Error: {str(e)}")