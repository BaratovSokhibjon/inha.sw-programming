import urllib.parse
import requests

class Geocoding:
    def __init__(self, graphhopper_api_key: str):
        self.ghr_api_key = graphhopper_api_key
        print(f"Initialized Geocoding with API key: {self.ghr_api_key}")

    def geocoding(self, location):

        while location == "":
            location = input("Enter the location again: ")

        geocode_url = "https://graphhopper.com/api/1/geocode?"
        url = geocode_url + urllib.parse.urlencode(
            {"q": location, "limit": "1", "key": self.ghr_api_key}
        )
        replydata = requests.get(url)
        json_data = replydata.json()
        json_status = replydata.status_code

        if json_status == 200 and len(json_data["hits"]) != 0:
            lat = json_data["hits"][0]["point"]["lat"]
            lng = json_data["hits"][0]["point"]["lng"]
            name = json_data["hits"][0]["name"]
            value = json_data["hits"][0]["osm_value"]
            country = json_data["hits"][0].get("country", "")
            state = json_data["hits"][0].get("state", "")

            if state and country:
                new_loc = f"{name}, {state}, {country}"
            elif state:
                new_loc = f"{name}, {country}"
            else:
                new_loc = name

            print(
                f"🌍 Geocoding API URL for {new_loc} (Location Type: {value})\n{url}"
            )
        else:
            lat = "null"
            lng = "null"
            new_loc = location
            if json_status != 200:
                print("❌ Error: " + str(json_status))
                print("❌ Geocode API status: " + str(json_status) +
                    "\nError message: " + json_data["message"])
        return json_status, lat, lng, new_loc
