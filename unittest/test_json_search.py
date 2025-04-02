import unittest
from recursive_json_search import *
from test_data import *

class JsonSearchTest(unittest.TestCase):
    def test_search_found(self):
        """Test if existing key is found"""
        self.assertTrue(json_search("issueSummary", data))
    
    def test_return_type(self):
        """Test if return value is a list"""
        self.assertIsInstance(json_search("issueSummary", data), list)
    
    def test_search_not_found(self):
        """Test non-existent key returns empty list"""
        self.assertEqual(json_search("bad_key", data), [])

if __name__ == '__main__':
    unittest.main()