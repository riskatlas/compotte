# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CompotteRequest
                                 A QGIS plugin
 Compotte server composition and layer styles with local repository
                             -------------------
        begin                : 2013-11-15
        copyright            : (C) 2013 by Jan Bojko
        email                : jan.bojko@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import requests,sys
from requests.auth import HTTPBasicAuth
from requests import Request, Session
import BeautifulSoup

class CompotteRequest:
    
    GEOSERVER_PATH = "/geoserver"
    CASSERVER_PATH = "/cas-server"
    #casHeaders = {'User-Agent': 'Mozilla/5.0'}
    casHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
    }
    
    def __init__(self,url,username=None,password=None,proxies=None,cas=False):
        
        self.setResources(url)
        
        if username and password:
            self.auth = HTTPBasicAuth(username,password)
        else:
            self.auth = None
        
        if proxies:
            self.proxies = proxies
        else:
            self.proxies = None
        
        if cas==True:
            self.session = Session()
            self.cas = True
            self.connectCas(username,password,proxies)
        else:
            self.cas = False
    
    def connectCas(self,username,password,proxies):
        url = self.casresource + "/login?service=" + self.serviceUrl + "/web"

        response = self.session.post(url, verify=False,proxies=self.proxies,headers=self.casHeaders)

        soup = BeautifulSoup.BeautifulSoup(response.content)
        ltdict = soup.find("input", {"name": "lt"})
        executiondict = soup.find("input", {"name": "execution"})
        lt = ltdict['value']
        execution = executiondict['value']

        self.payload = {'_eventId': 'submit', 'lt': lt,'execution': execution, 'submit': 'LOGIN', 'username': username, 'password': password}
        response = self.session.post(url, data=self.payload,proxies=self.proxies,verify=False,headers=self.casHeaders,allow_redirects=True)
        self.casCookies = response.cookies
    
    def sendRequest(self,url, stream = False):        
        if self.cas==True:
            response = self.session.get(url, proxies=self.proxies,cookies=self.casCookies, stream=stream, verify=False)
        else:
            response = requests.get(url,auth=self.auth,proxies=self.proxies,stream=stream,verify=False)

        return response
    
    def setResources(self,url):
        
        if len(url) == 0:
            raise requests.exceptions.URLRequired("Requested URL is empty!")
                
        self.serviceUrl = url.strip().rstrip('/') + self.GEOSERVER_PATH
        self.serviceUrl80 = url.strip().rstrip('/') + ':80' + self.GEOSERVER_PATH
        self.casresource = url.strip().rstrip('/') + self.CASSERVER_PATH
        self.casresource = self.casresource.replace("http","https").rstrip('/') 
        self.wfsresource = self.serviceUrl.rstrip('/') + "/ows"
        self.restresource = self.serviceUrl.rstrip('/') + "/rest"
        
        return
    
    @staticmethod
    def parseWorkspaceFromURL(url,serviceUrl):
        
        if serviceUrl == "" or serviceUrl == False:
            return ""
        
        userUrl = serviceUrl.strip("/")
        workspace = url.replace(userUrl,'').strip("/")
        end = workspace.find('/')
        workspace = workspace[0:end]
        return workspace