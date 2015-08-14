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
from ui_service import Ui_Service

class ServiceDialog(QtGui.QDialog):

    def __init__(self,parent,edit=False):
        QtGui.QDialog.__init__(self)
        self.parent = parent

        self.ui = Ui_Service()
        self.ui.setupUi(self)
        self.edit = edit
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        self.ui.buttonBox.accepted.connect(self.saveSettings)
        QtCore.QObject.connect(self.ui.name, QtCore.SIGNAL("textChanged(QString)"), self.checkNoEmptyName)
        QtCore.QObject.connect(self.ui.cmdBrowseComposition, QtCore.SIGNAL("clicked()"), self.loadTempDir)
        QtCore.QObject.connect(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Help), QtCore.SIGNAL("clicked()"), self.showHelp)

    def saveSettings(self):
        settings = self.parent.settings

        name = self.ui.name.text()
        service = self.ui.serviceUrl.text()
        username = self.ui.username.text()
        password = self.ui.password.text()
        chkCas = self.ui.checkBox.isChecked()
        filePath = self.ui.filePath.text()

        settings.setValue("compotte/name_" + name, name)
        settings.setValue("compotte/service_" + name, service)
        settings.setValue("compotte/username_" + name, username)
        settings.setValue("compotte/password_" + name, password)
        settings.setValue("compotte/cas_" + name, str(chkCas))
        settings.setValue("compotte/dir_" + name, filePath)

        if self.edit == False:
            self.parent.ui.cmbService.addItem(name,name)

    def fill(self):
        settings = self.parent.settings

        name = self.parent.ui.cmbService.currentText()
        service = settings.value("compotte/service_" + name)
        username = settings.value("compotte/username_" + name)
        password = settings.value("compotte/password_" + name)
        cas = settings.value("compotte/cas_" + name)
        cas = self.parent.str2bool(cas)
        dir = settings.value("compotte/dir_" + name)

        self.ui.name.setText(name)
        self.ui.name.setReadOnly(True)
        self.ui.serviceUrl.setText(service)
        self.ui.username.setText(username)
        self.ui.password.setText(password)
        self.ui.checkBox.setChecked(cas)
        self.ui.filePath.setText(dir)

    def loadTempDir(self):
        tempDirectory = QtGui.QFileDialog.getExistingDirectory(self, "Temp directory", "", QtGui.QFileDialog.ShowDirsOnly)
        self.ui.filePath.setText(tempDirectory)

    def checkNoEmptyName(self):
        if not self.ui.name.text().strip() == "":
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        if self.edit == False:
            name = self.ui.name.text()

            for idx in range(0,self.parent.ui.cmbService.count()):
                if self.parent.ui.cmbService.itemText(idx) == name:
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)


    def showHelp(self):
        help_file = "http://redmine.ccss.cz/projects/compotte/wiki"
        # For testing path:
        #QMessageBox.information(None, "Help File", help_file)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(help_file))
