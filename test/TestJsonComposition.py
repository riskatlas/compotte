import unittest
import requests

class TestJsonComposition(unittest.TestCase):

    def setUp(self):
        #URL path to the tested composition
        self.compositionURL = 'http://localhost/kompozice.json'

    def test_getURL(self):
        response = requests.get(self.compositionURL)
        self.assertEqual(response.status_code, 200)

    def test_getContentType(self):
    	response = requests.get(self.compositionURL)
    	headers = response.headers['content-type']
        self.assertEqual(headers, 'application/json')

    def test_getJson(self):
    	response = requests.get(self.compositionURL)
    	json = response.json()
    	self.assertNotEqual(json['data']['layers'][0], '');

if __name__ == '__main__':
    unittest.main()

