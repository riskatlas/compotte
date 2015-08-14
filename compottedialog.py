# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CompotteDialog
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

from PyQt4 import QtCore, QtGui
from ui_compotte import Ui_Compotte
from qgis.core import *
from collections import deque
from compotterequest import CompotteRequest
import requests

import os, os.path, tempfile, sys
from servicedialog import ServiceDialog
import json
import re
from xml.etree import ElementTree
import wfs20lib
import random, string
import qgis
from os.path import abspath, exists

class CompotteDialog(QtGui.QDialog):

    def __init__(self,parent):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.parent = parent
        
        self.ui = Ui_Compotte()
        self.ui.setupUi(self)
        
        self.settings = QtCore.QSettings()
        
        keys = self.settings.allKeys()
        for key in keys:
            if key.startswith("compotte/name"):
                name = self.settings.value(key)
                self.ui.cmbService.addItem(name,name)
        
        self.vendorparameters = ""
        
        self.externalWMSQueue = deque()
        self.downloadQueue = deque()
        
        QtCore.QObject.connect(self.ui.cmdGetCapabilities, QtCore.SIGNAL("clicked()"), self.getLayersCapabilities)
        QtCore.QObject.connect(self.ui.cmbFeatureType, QtCore.SIGNAL("currentIndexChanged(int)"), self.update_ui)
        QtCore.QObject.connect(self.ui.cmdGetFeature, QtCore.SIGNAL("clicked()"), self.downloadLayers)
        QtCore.QObject.connect(self.ui.cmdBrowseComposition, QtCore.SIGNAL("clicked()"), self.loadCompositionFromFileSystem)
        QtCore.QObject.connect(self.ui.cmdAddComposition, QtCore.SIGNAL("clicked()"), self.addComposition)
        QtCore.QObject.connect(self.ui.cmdCheckComposition, QtCore.SIGNAL("clicked()"), self.checkComposition)
        QtCore.QObject.connect(self.ui.cmdCancel, QtCore.SIGNAL("clicked()"), self.cancelDownload)
        QtCore.QObject.connect(self.ui.cmdNew, QtCore.SIGNAL("clicked()"), self.showServiceDialog)
        QtCore.QObject.connect(self.ui.cmdEdit, QtCore.SIGNAL("clicked()"), self.editService)
        QtCore.QObject.connect(self.ui.cmdDelete, QtCore.SIGNAL("clicked()"), self.deleteServiceEntry)
    
    def init_variables(self):
        self.featuretypes = {}
        self.featurestyles = {}
        self.querystatus = ""
        self.lastAddedLayer = None

        service,username,password,cas = self.getConnectionSettings()
        self.compotteRequest = CompotteRequest(service,username,password,self.getProxy(),cas)

    def getConnectionSettings(self):
        name = self.ui.cmbService.currentText()
        service = self.settings.value("compotte/service_" + name).strip()
        username = self.settings.value("compotte/username_" + name).strip()
        password = self.settings.value("compotte/password_" + name).strip()
        cas = self.settings.value("compotte/cas_" + name)
        cas = self.str2bool(cas)

        return service,username,password,cas

    def getNameAndLink(self,root,namespace):
        
        defaultStyle = root.find("defaultStyle".format(namespace))
        
        defaultStyleLink = defaultStyle.findall("{0}link".format(namespace))
        
        sldName = defaultStyle.find("name").text
        sldLink = defaultStyleLink[0].attrib.get("href")
        sldCorrectLink = sldLink.rstrip(".xml") + ".sld"
        
        return (sldName,sldCorrectLink)
    
    def getLayerStyles(self,layername):
        namespace = "{http://www.w3.org/2005/Atom}"
        #URL FIX
        restresource = self.compotteRequest.wfsresource.rstrip('/')
        #Fixme
        restresource = self.compotteRequest.restresource + "/layers/{0}.{1}".format(layername,"xml")

        try:
            bufferSLDAddress = self.sendRequest(restresource).content
        except:
                return 
        
        if (bufferSLDAddress != None):
            # process Response
            try:
                root = ElementTree.fromstring(bufferSLDAddress)
                if self.is_restlayer_styles(root):
    
                    defaultStyle = root.find("defaultStyle".format(namespace))
            
                    defaultStyleLink = defaultStyle.find("{0}link".format(namespace))
                    
                    sldName = defaultStyle.find("name").text
                    sldLink = defaultStyleLink.attrib.get("href")
                    sldCorrectLink = sldLink.rstrip(".xml") + ".sld"
                    
                    self.featurestyles[sldName] = sldCorrectLink
                    self.ui.cmbStyle.addItem(sldName)
                    
                    for target in root.findall("styles/style".format(namespace)):
                        sldName = target.find("name").text
                        styleLink = target.find("{0}link".format(namespace))
                        sldLink = styleLink.attrib.get("href")
                        sldCorrectLink = sldLink.rstrip(".xml") + ".sld"
                        
                        self.featurestyles[sldName] = sldCorrectLink
                        self.ui.cmbStyle.addItem(sldName)
            except ElementTree.ParseError, e:
                QtGui.QMessageBox.critical(self, "Downloading style", "Not a valid OnlineResource! Try authenticate.")
        
        self.logMessage(restresource)
    
    def getCompositionJson(self):
        if not self.ui.compositionURL.text().strip() == "":
            compositionURL = self.ui.compositionURL.text().strip()
            try:
                response = self.sendRequest(compositionURL)
            except:
                return 
            output = response.json()
        elif not self.ui.filePath.text() == "":
            json_data = open(self.ui.filePath.text()).read()
            output = json.loads(json_data)
        
        return output
    
    #TODO
    def checkComposition(self):
        try:
            self.init_variables()
        except requests.exceptions.URLRequired, e:
            QtGui.QMessageBox.critical(self, 'Error', 'A valid URL is required to make a request.')
            return

        self.ui.tableWidget.clear()
        
        if not (self.ui.compositionURL.text() == "" and self.ui.filePath.text() == ""):
            self.composition = self.getCompositionJson()
            self.ui.lblMessage.setText("")
        else:
            self.ui.lblMessage.setText("A Composition is not defined!")
            return
        
        layersNum = len(self.composition['layers'])
        
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(3)
        
        
        nameHead = QtGui.QTableWidgetItem('Name')
        statusHead = QtGui.QTableWidgetItem('Status')
        downloadedHead = QtGui.QTableWidgetItem('Downloaded')
        bar = QtGui.QProgressBar()
        bar.setTextVisible(False)
    
        self.ui.tableWidget.setHorizontalHeaderItem(0,nameHead)
        self.ui.tableWidget.setHorizontalHeaderItem(1,statusHead)
        self.ui.tableWidget.setHorizontalHeaderItem(2,downloadedHead)
        self.ui.tableWidget.setColumnWidth(0,225)
        
        i = 0
        for layer in self.composition['layers']:
            #table
            try:       
                url = self.getSomeURLFromLayer(layer)
                if self.checkURLInLayer(layer):
                    serviceUrl = self.checkURLInLayer(layer)
                    self.ui.tableWidget.insertRow(i)
                    if 'title' in layer:
                        item = QtGui.QTableWidgetItem(layer['title'])
                    else:
                        item = QtGui.QTableWidgetItem(layer['name'])
                        layer['title'] = layer['name']
                    
                    item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.ui.tableWidget.setItem(i,0, item)
                
                    self.ui.tableWidget.setItem(i,1, QtGui.QTableWidgetItem('Download..'))
                    self.ui.tableWidget.setCellWidget(i,2, QtGui.QProgressBar())
                    # style
                    if 'style' in layer:
                        style = layer['style']
                    elif 'name' in layer['metadata']['styles'][0]:
                        style = layer['metadata']['styles'][0]['name']
                    elif 'STYLES' in layer['params']:
                        style = layer['params']['STYLES']
                    # workspace
                    workspace = CompotteRequest.parseWorkspaceFromURL(url,serviceUrl)
                    # geoserver name
                    layername = layer['params']['LAYERS']
                    self.downloadQueue.append([workspace + ":" + layername,style,workspace,self.composition['projection'],i])
                else:
                    #TODO
                    self.ui.tableWidget.setItem(i,1, QtGui.QTableWidgetItem('External WMS'))
                    self.externalWMSQueue.append([layer['name'],layer['capabilitiesURL'],layer['workspace']])
            except KeyError, e:
                continue
                self.logMessage('I got a KeyError - reason "%s"' % str(e))
                
            i = i + 1
        
        self.ui.cmdAddComposition.setEnabled(True)
    
    def checkURLInLayer(self,layer):
        url = self.getSomeURLFromLayer(layer)

        if not url.find(self.compotteRequest.serviceUrl) == -1: 
            return self.compotteRequest.serviceUrl
        elif not url.find(self.compotteRequest.serviceUrl80) == -1:
            return self.compotteRequest.serviceUrl80
        else:
            return False

    def getSomeURLFromLayer(self,layer):
        if 'capabilitiesURL' in layer:
            url = layer['capabilitiesURL']
        else:
            url = layer['url']
            
        return url
    
    def addComposition(self):
        try:
            self.init_variables()
        except requests.exceptions.URLRequired, e:
            QtGui.QMessageBox.critical(self, 'Error', 'A valid URL is required to make a request.')
            return

        if not any(self.composition):
             self.ui.lblMessage.setText("Composition empty. Try check the resource URL.")
             return

        legend = self.parent.iface.legendInterface()

        self.compositionGroup = legend.addGroup(self.composition['title'], False )
        tempWorkspace = []
        workspace = {}
        self.layerRelatedGroupId = {}
        
        for layer in self.composition['layers']:
            try:
                url = self.getSomeURLFromLayer(layer)
                serviceUrl = self.checkURLInLayer(layer)
                layerWorkspace = CompotteRequest.parseWorkspaceFromURL(url,serviceUrl)
                
                if self.checkURLInLayer(layer):
                        if len(tempWorkspace) == 0 or not tempWorkspace.__contains__(layerWorkspace):
                            grpIdx = legend.addGroup(layerWorkspace, False, self.compositionGroup)
                            workspace[layerWorkspace] = grpIdx
                            tempWorkspace.append(layerWorkspace)
                        self.layerRelatedGroupId[layerWorkspace + ":" + layer['params']['LAYERS']] = workspace[layerWorkspace]
            except KeyError, e:
                    continue

        self.querystatus = 'Ready'
        
        self.downloadLayers()
        
    def loadCompositionFromFileSystem(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Open composition", "", "JSON (*.json);;Composition (*.hsl)")
        self.ui.filePath.setText(fileName)
    
    def clearCompositions(self):
        self.externalWMSQueue.clear()
        self.downloadQueue.clear()
        self.tempDownload = []
    
    # Process GetCapabilities-Request
    def getLayersCapabilities(self):
        self.reset()
        try:
            self.init_variables()
        except requests.exceptions.URLRequired, e:
            QtGui.QMessageBox.critical(self, 'Error', 'A valid URL is required to make a request.')
            return
        self.clearCompositions()
        self.ui.cmdGetFeature.setEnabled(False);
        self.ui.txtSrs.setText("EPSG:{0}".format(str(self.parent.iface.mapCanvas().mapRenderer().destinationCrs().postgisSrid())))

        if "?" in self.compotteRequest.wfsresource:
            request = "{0}{1}".format(self.compotteRequest.wfsresource, self.fix_acceptversions(self.compotteRequest.wfsresource, "&"))
        else: 
            request = "{0}{1}".format(self.compotteRequest.wfsresource, self.fix_acceptversions(self.compotteRequest.wfsresource, "?"))

        self.logMessage(request)
        
        try:
            buffer = self.sendRequest(request).content
        except:
            return
    
        if (buffer != None):
            # process Response
            try:
                root = ElementTree.fromstring(buffer)
            except:
                QtGui.QMessageBox.critical(self, "Bad URL", "Corrupted XML format. Are you using right Portal URL? Are you authenticated?")
                self.reset()
                return
            if self.is_wfs20_capabilities(root):
                # WFS 2.0 Namespace
                nswfs = "{http://www.opengis.net/wfs/2.0}"
                nsxlink = "{http://www.w3.org/1999/xlink}"
                nsows = "{http://www.opengis.net/ows/1.1}"
                # GetFeature OnlineResource
                for target in root.findall("{0}OperationsMetadata/{0}Operation".format(nsows)):
                    if target.get("name") == "GetFeature":                        
                        for subtarget in target.findall("{0}DCP/{0}HTTP/{0}Get".format(nsows)):
                            getfeatureurl = subtarget.get("{0}href".format(nsxlink))
                            if not "?" in getfeatureurl:
                                self.compotteRequest.wfsresource = getfeatureurl
                            else:
                                self.compotteRequest.wfsresource = getfeatureurl[:getfeatureurl.find("?")]
                                self.vendorparameters = getfeatureurl[getfeatureurl.find("?"):].replace("?", "&")
                for target in root.findall("{0}FeatureTypeList/{0}FeatureType".format(nswfs)):
                    for name in target.findall("{0}Name".format(nswfs)):
                        self.ui.cmbFeatureType.addItem(name.text,name.text)
                        featuretype = wfs20lib.FeatureType(name.text)                        
                        if ":" in name.text:
                            nsmap = self.get_namespace_map(buffer)
                            for prefix in nsmap:
                                if prefix == name.text[:name.text.find(":")]:
                                    featuretype.setNamespace(nsmap[prefix])
                                    featuretype.setNamespacePrefix(prefix)
                                    break
                        for title in target.findall("{0}Title".format(nswfs)):
                            featuretype.setTitle(title.text)
                        for abstract in target.findall("{0}Abstract".format(nswfs)):
                            featuretype.setAbstract(abstract.text)
                        for metadata_url in target.findall("{0}MetadataURL".format(nswfs)):
                            featuretype.setMetadataUrl(metadata_url.get("{0}href".format(nsxlink)))
                        self.featuretypes[name.text] = featuretype
                        self.querystatus = "Ready"
                self.update_ui()

    def lock_ui(self):
        self.ui.cmdGetCapabilities.setEnabled(False)
        self.ui.cmdGetFeature.setEnabled(False)
        self.ui.cmbFeatureType.setEnabled(False)

    def unlock_ui(self):
        self.ui.cmdGetCapabilities.setEnabled(True)
        self.ui.cmdGetFeature.setEnabled(True)
        self.ui.cmbFeatureType.setEnabled(True)

    def reset(self):
        self.featuretypes = {}
        self.featurestyles = {}
        self.querystatus = ""
        self.lastAddedLayer = None
        self.ui.cmbStyle.clear()
        self.ui.cmbFeatureType.clear()
        self.ui.lblMessage.setText("")
        self.ui.txtFeatureTypeTitle.setPlainText("")
        self.ui.txtFeatureTypeDescription.setPlainText("")
        self.ui.txtSrs.setText("")

    # UI: Update Parameter-Frame
    def update_ui(self):      
        if self.querystatus == "Ready":
            featuretype = self.featuretypes[self.ui.cmbFeatureType.currentText()]
            self.ui.cmbStyle.clear()
            self.featurestyles.clear()
            self.getLayerStyles(self.ui.cmbFeatureType.currentText())
    
            if featuretype.getTitle():
                if len(featuretype.getTitle()) > 0:
                    self.ui.txtFeatureTypeTitle.setVisible(True)
                    self.ui.txtFeatureTypeTitle.setPlainText(featuretype.getTitle())
                else:
                    self.ui.txtFeatureTypeTitle.setVisible(False)
            else: 
                self.ui.txtFeatureTypeTitle.setVisible(False)
    
            if featuretype.getAbstract():
                if len(featuretype.getAbstract()) > 0:
                    self.ui.txtFeatureTypeDescription.setVisible(True)
                    self.ui.txtFeatureTypeDescription.setPlainText(featuretype.getAbstract())
                else:
                    self.ui.txtFeatureTypeDescription.setVisible(False)
            else: 
                self.ui.txtFeatureTypeDescription.setVisible(False)
    
            self.ui.cmdGetFeature.setEnabled(True)
            self.ui.lblMessage.setText("")
            
    def str2bool(self,v):
        return v.lower() in ("yes", "true", "t", "1")

        # check for OWS-Exception
    def is_exception(self, root):
        for namespace in ["{http://www.opengis.net/ows}", "{http://www.opengis.net/ows/1.1}"]:
        # check correct Rootelement
            if root.tag == "{0}ExceptionReport".format(namespace):  
                for exception in root.findall("{0}Exception".format(namespace)):
                    for exception_text in exception.findall("{0}ExceptionText".format(namespace)):
                        QtGui.QMessageBox.critical(self, "OWS Exception", "OWS Exception returned from the WFS:<br>"+ str(exception_text.text))
                        self.ui.lblMessage.setText("")
                return True
        return False
        
    def is_restlayer_styles(self,root):
        if root.tag == "layer":  
            return True
        QtGui.QMessageBox.critical(self, "Error", "Not a valid WFS GetCapabilities-Response!")
        self.ui.lblMessage.setText("")
        return False
    
    # Check for empty GetFeature result
    def is_empty_response(self, root):
        # deegree 3.2: numberMatched="unknown" does return numberReturned="0" instead of numberReturned="unknown"
        # https://portal.opengeospatial.org/files?artifact_id=43925
        if not root.get("numberMatched") == "unknown": 
            # no Features returned?
            if root.get("numberReturned") == "0":
                return True
        return False
    
    # check for correct WFS version (only WFS 2.0 supported)
    def is_wfs20_capabilities(self, root):
        if self.is_exception(root):
            return False
        if root.tag == "{0}WFS_Capabilities".format("{http://www.opengis.net/wfs/2.0}"):  
            return True
        if root.tag == "{0}WFS_Capabilities".format("{http://www.opengis.net/wfs}"):  
            QtGui.QMessageBox.warning(self, "Wrong WFS Version", "This Plugin has dedicated support for WFS 2.0!")
            self.ui.lblMessage.setText("")
            return False
        QtGui.QMessageBox.critical(self, "Error", "Not a valid WFS GetCapabilities-Response!")
        self.ui.lblMessage.setText("")
        return False
        
    def save_tempfile(self, filename, content):
        tmpfile = get_temppath(filename)
        fobj = open(tmpfile,'wb')
        fobj.write(content)
        fobj.close()  
        return tmpfile
    
    def logMessage(self, message):
        if globals().has_key('QgsMessageLog'):
            QgsMessageLog.logMessage(message, "Compotte")
    
        # Hack to fix version/acceptversions Request-Parameter
    def fix_acceptversions(self, onlineresource, connector):
        return "{0}service=WFS&acceptversions=2.0.0&request=GetCapabilities".format(connector)
    
    def getTempPath(self, filename):

        name = self.ui.cmbService.currentText()
        dirPath = self.settings.value("compotte/dir_" + name)
        if dirPath.strip() == "":
            tmpdir = os.path.join(tempfile.gettempdir(),'Compotte')
        else:
            tmpdir = os.path.join(dirPath,'Compotte')
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        tmpfile= os.path.join(tmpdir, filename)
        return tmpfile
                
    # Determine namespaces in the capabilities (including non-used)
    def get_namespace_map(self, xml):
        nsmap = {}
        for i in [m.start() for m in re.finditer('xmlns:', xml)]:
            j = i + 6
            prefix = xml[j:xml.find("=", j)]
            k = xml.find("\"", j)
            uri = xml[k + 1:xml.find("\"", k + 1)]

            prefix = prefix.strip()
            # uri = uri.replace("\"","")
            uri = uri.strip()
            # text+= prefix + " " + uri + "\n"
 
            nsmap[prefix] = uri
        return nsmap
        
    # Receive Proxy from QGIS-Settings
    def getProxy(self):
        if self.settings.value("/proxy/proxyEnabled") == "true":
           proxy = "{0}:{1}".format(self.settings.value("/proxy/proxyHost"), self.settings.value("/proxy/proxyPort"))
           if proxy.startswith("http://"):
               return proxy
           else:
               return proxy
        else: 
            return None
        
    # Process GetFeature-Request
    def downloadLayers(self):
        self.tempDownload = []
        self.ui.cmdCancel.setEnabled(True)
        self.ui.lblMessage.setText("Please wait while downloading!")

        if self.querystatus == "Ready":
            
            if len(self.downloadQueue) == 0:
                featuretype = self.ui.cmbFeatureType.currentText()
                srsName = self.ui.txtSrs.text().strip()
            else:
                self.tempDownload = self.downloadQueue.popleft()
                featuretype = self.tempDownload[0]
                srsName = self.tempDownload[3]
                
            query_string = "?service=WFS&request=GetFeature&version=2.0.0&srsName={0}&typeNames={1}".format(srsName, featuretype)

        query_string+=self.vendorparameters
        query_string+="&outputFormat=SHAPE-ZIP"
        self.logMessage(self.compotteRequest.wfsresource + query_string)

        self.httpGetId = 0
        self.httpRequestAborted = False
        
        layername="wfs{0}".format(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)))
        self.downloadFile(self.compotteRequest.wfsresource, query_string, self.getTempPath("{0}.zip".format(layername)))

        
    #############################################################################################################
    # Requests
    #############################################################################################################

    def downloadFile(self, onlineResource, queryString, fileName):
        self.lock_ui()
        
        url = QtCore.QUrl(onlineResource.replace("http","https"))

        if QtCore.QFile.exists(fileName):
            QtCore.QFile.remove(fileName)
        
        with open(fileName,'wb') as self.outFile:
            try:
                response = self.sendRequest('https://' + url.host() + url.path() + queryString, stream=True)
            except:
                return
            
            if self.checkStatusCode(response.status_code):
                return
            kilobytes = 0 
            for block in response.iter_content(1024):
                if not block:
                    break
                kilobytes = kilobytes + 1    
                self.updateDataReadProgress(kilobytes, 0)
                self.outFile.write(block)
            self.httpRequestFinished()

    # Currently unused
    def cancelDownload(self):
        self.httpRequestAborted = True
        self.close()

        self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setValue(0)
        self.unlock_ui()

    def deleteServiceEntry(self):

        if self.ui.cmbService.count() > 0:
            quit_msg = "Are you sure you want to delete current entry?"
            reply = QtGui.QMessageBox.question(self, 'Confirmation',
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                name = self.ui.cmbService.currentText()
                self.settings.remove("compotte/name_" + name)
                self.settings.remove("compotte/service_" + name)
                self.settings.remove("compotte/username_" + name)
                self.settings.remove("compotte/password_" + name)
                self.settings.remove("compotte/cas_" + name)
                self.settings.remove("compotte/dir_" + name)
                idx = self.ui.cmbService.currentIndex()
                self.ui.cmbService.removeItem(idx)

    def showServiceDialog(self):
        self.dialog = ServiceDialog(self)
        self.dialog.show()

    def editService(self):
        if self.ui.cmbService.count() > 0:
            self.dialog = ServiceDialog(self,True)
            self.dialog.fill()
            self.dialog.show()

    # Add layer to the QGIS
    def httpRequestFinished(self):
        if self.httpRequestAborted:
            if self.outFile is not None:
                self.outFile.close()
                self.outFile.remove()
                self.outFile = None
            return

        self.outFile.close()

        self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setValue(1)

        if (self.outFile.name.find(".zip") != -1):   
            
            if not self.ui.cmbStyle.currentText() == "" or not self.tempDownload[1] == "":
                
                if len(self.tempDownload) == 0:
                    self.loadVectorLayer(str(self.outFile.name), self.ui.cmbFeatureType.currentText())
                    stylename = self.ui.cmbStyle.currentText()
                else:
                    self.loadVectorLayer(str(self.outFile.name), self.tempDownload[0])
                    stylename = self.tempDownload[1]
                    layername = self.tempDownload[0]
                    self.getLayerStyles(layername)
                
                #TODO
                try:
                    featurestyle = self.featurestyles[stylename]
                except:
                    self.ui.lblMessage.setText("Downloading failed. Are layers available on the server ?")
                    self.unlock_ui()
                    return
                
                styleFilePath = str(self.getTempPath("{0}.sld".format(stylename)))
                
                if featurestyle:
                    with open(self.getTempPath(styleFilePath), 'wb') as handle:
                        try:
                            request = self.sendRequest(featurestyle, stream=True)
                        except:
                            return
                        for block in request.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)

                if not self.lastAddedLayer is None:
                    self.lastAddedLayer.loadSldStyle(styleFilePath)
                    legend = self.parent.iface.legendInterface()
                    legend.refreshLayerSymbology(self.lastAddedLayer)
                    self.parent.iface.mapCanvas().refresh()
                    
        elif (self.outFile.fileName().find(".sld") != -1):
            self.lastAddedLayer.loadSldStyle(str(self.outFile.name))

        self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setValue(0)
        if not len(self.tempDownload) == 0:
            bar = self.ui.tableWidget.cellWidget(self.tempDownload[4],2)
            status = self.ui.tableWidget.item(self.tempDownload[4],1)
            if not status.text() == "Failed!": 
                status.setText('Done!')
                bar.setMaximum(1)
                bar.setValue(1)
        
        self.unlock_ui()
        if not len(self.downloadQueue) == 0:
            self.downloadLayers()

    def sendRequest(self,url,stream=False):
        try:
            response = self.compotteRequest.sendRequest(url,stream)
        except requests.exceptions.HTTPError, e:
            QtGui.QMessageBox.critical(self, 'Error', 'HTTP ERROR %s occured' % e.code)
        except requests.exceptions.URLRequired, e:
            QtGui.QMessageBox.critical(self, 'Error', 'A valid URL is required to make a request. \n Is this URL correct: %s ?' % service)
        except requests.exceptions.ConnectionError, e:
            name = self.ui.cmbService.currentText()
            service = self.settings.value("compotte/service_" + name)
            QtGui.QMessageBox.critical(self, 'Error', 'Cannot proceed! Maybe bad resource URL? \n Is this URL correct: %s ?' % service)
        else:
            return response
    
    def checkStatusCode(self, statusCode):
        error = False
        # Check for genuine error conditions.
        if statusCode not in (200, 300, 301, 302, 303, 307):
            QtGui.QMessageBox.critical(self, 'Error',
                    'Download failed. Error %s' % str(statusCode))
            self.ui.lblMessage.setText("")
            self.httpRequestAborted = True
            error = True
        return error

    def updateDataReadProgress(self, bytesRead, totalBytes):
        if self.httpRequestAborted:
            return
        self.ui.progressBar.setMaximum(totalBytes)
        self.ui.progressBar.setValue(bytesRead)
        self.ui.lblMessage.setText("Please wait while downloading - {0} KB downloaded!".format(str(bytesRead)))
        
        if not len(self.tempDownload) == 0:
            bar = self.ui.tableWidget.cellWidget(self.tempDownload[4],2)
            bar.setMaximum(totalBytes)
            bar.setValue(bytesRead)

    def loadVectorLayer(self, filename, layername):
        self.ui.lblMessage.setText("Loading {0}".format(filename));
        vlayer = QgsVectorLayer(filename, layername, "ogr")    
        vlayer.setProviderEncoding("UTF-8") #Ignore System Encoding --> TODO: Use XML-Header        
        if not vlayer.isValid():
            if len(self.tempDownload) == 0:
                QtGui.QMessageBox.critical(self, "Error", "Response is not a valid QGIS-Layer! \n Layername: " + layername)
                self.ui.lblMessage.setText("")
            else:
                status = self.ui.tableWidget.item(self.tempDownload[4],1)
                bar = self.ui.tableWidget.cellWidget(self.tempDownload[4],2)
                status.setText('Failed!')
                bar.setMaximum(1)
                bar.setValue(0)
        else: 
            self.ui.lblMessage.setText("")
            # QGIS 1.8, 1.9
            if hasattr(QgsMapLayerRegistry.instance(), "addMapLayers"):
                QgsMapLayerRegistry.instance().addMapLayers([vlayer])
            # QGIS 1.7
            else:
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            self.parent.iface.zoomToActiveLayer()
            
            legend = self.parent.iface.legendInterface()
            if not len(self.tempDownload) == 0:
                legend.moveLayer(vlayer,self.layerRelatedGroupId[layername])
            self.lastAddedLayer = vlayer
