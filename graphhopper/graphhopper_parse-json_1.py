import requests
import urllib.parse
import yaml

config = yaml.safe_load(open("config.yml"))

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
#loc1 = "Washington, D.C."
loc1 = "Rome, Italy"
loc2 = "Baltimore, Maryland"
key = config["api_key"]

url = geocode_url + urllib.parse.urlencode({"q":loc1, "limit": "1", "key":key})

replydata = requests.get(url)
json_data = replydata.json()
json_status = replydata.status_code
print(json_data)