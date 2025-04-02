from test_data import *

def json_search(key, input_object):
    ret_val = []
    def inner_function(key, input_object):
        if isinstance(input_object, dict):
            for k, v in input_object.items():
                if k == key:
                    ret_val.append({k: v})
                if isinstance(v, (dict, list)):
                    inner_function(key, v)
        elif isinstance(input_object, list):
            for item in input_object:
                if isinstance(item, (dict, list)):
                    inner_function(key, item)
    inner_function(key, input_object)
    return ret_val