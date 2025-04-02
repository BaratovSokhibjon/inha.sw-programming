import yaml

def parse_yaml(yaml_string):
    try:
        return yaml.safe_load(yaml_string)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return None