import json

def parse_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None