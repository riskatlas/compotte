import unittest
import httpretty
import requests
import sys,os
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from compotterequest import CompotteRequest

class TestCompotteRequest(unittest.TestCase):

    def setUp(self):
        #URL path to the tested composition
        self.portalUrl = "http://erra.pprd-east.eu"
        self.geoserverUrl = "http://erra.pprd-east.eu/geoserver"
        self.geoserverUrlPort = "http://erra.pprd-east.eu:80/geoserver"
        self.serviceUrl = 'http://erra.pprd-east.eu/geoserver/gecp/ows?SERVICE=WMS&'
        self.serviceUrl80 = 'http://erra.pprd-east.eu:80/geoserver/gecp/ows?SERVICE=WMS&'

    def test_parseWorkspaceFromURL(self):
        workspace = CompotteRequest.parseWorkspaceFromURL(self.serviceUrl,self.geoserverUrl)
        self.assertEqual(workspace,"gecp")
    
    def test_parseWorkspaceFromURLWithPort(self):
        workspace = CompotteRequest.parseWorkspaceFromURL(self.serviceUrl80,self.geoserverUrlPort)
        self.assertEqual(workspace,"gecp")
    
    def test_parseWorkspaceFromURLWithEmptyService(self):
        workspace = CompotteRequest.parseWorkspaceFromURL(self.serviceUrl,"")
        self.assertEqual(workspace,"")
    
    def test_setResources(self):
        compotteRequest = CompotteRequest("admin","geoserver",None)
        compotteRequest.setResources(self.portalUrl)
        self.assertEqual(compotteRequest.wfsresource,"http://erra.pprd-east.eu/geoserver/ows")
        self.assertEqual(compotteRequest.restresource,"http://erra.pprd-east.eu/geoserver/rest")
        self.assertEqual(compotteRequest.serviceUrl,"http://erra.pprd-east.eu/geoserver")
        self.assertEqual(compotteRequest.serviceUrl80,"http://erra.pprd-east.eu:80/geoserver")
        self.assertEqual(compotteRequest.casresource,"https://erra.pprd-east.eu/cas-server")
    
    #TODO
    @httpretty.activate
    def test_xml_response(self):
        httpretty.register_uri(httpretty.GET, "http://api.yipit.com/v1/deals/",
                           body='[{"title": "Test Deal"}]',
                           content_type="application/json")
        
        response = requests.get('http://api.yipit.com/v1/deals/')

        self.assertEqual(response.json(),[{"title": "Test Deal"}])

if __name__ == '__main__':
    unittest.main()

