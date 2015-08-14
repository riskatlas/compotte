# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_service.ui'
#
# Created: Mon Apr 28 14:47:44 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Service(object):
    def setupUi(self, Service):
        Service.setObjectName(_fromUtf8("Service"))
        Service.resize(438, 367)
        self.buttonBox = QtGui.QDialogButtonBox(Service)
        self.buttonBox.setGeometry(QtCore.QRect(70, 320, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(Service)
        self.label.setGeometry(QtCore.QRect(10, 0, 321, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.serviceUrl = QtGui.QLineEdit(Service)
        self.serviceUrl.setGeometry(QtCore.QRect(110, 86, 301, 21))
        self.serviceUrl.setObjectName(_fromUtf8("serviceUrl"))
        self.username = QtGui.QLineEdit(Service)
        self.username.setGeometry(QtCore.QRect(110, 116, 241, 21))
        self.username.setObjectName(_fromUtf8("username"))
        self.password = QtGui.QLineEdit(Service)
        self.password.setGeometry(QtCore.QRect(110, 146, 241, 21))
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.lblUrl = QtGui.QLabel(Service)
        self.lblUrl.setGeometry(QtCore.QRect(10, 80, 41, 31))
        self.lblUrl.setObjectName(_fromUtf8("lblUrl"))
        self.lblUsername = QtGui.QLabel(Service)
        self.lblUsername.setGeometry(QtCore.QRect(10, 110, 71, 31))
        self.lblUsername.setObjectName(_fromUtf8("lblUsername"))
        self.lblPassword = QtGui.QLabel(Service)
        self.lblPassword.setGeometry(QtCore.QRect(10, 140, 71, 31))
        self.lblPassword.setObjectName(_fromUtf8("lblPassword"))
        self.checkBox = QtGui.QCheckBox(Service)
        self.checkBox.setGeometry(QtCore.QRect(10, 190, 171, 22))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.cmdBrowseComposition = QtGui.QPushButton(Service)
        self.cmdBrowseComposition.setGeometry(QtCore.QRect(380, 260, 41, 21))
        self.cmdBrowseComposition.setObjectName(_fromUtf8("cmdBrowseComposition"))
        self.filePath = QtGui.QLineEdit(Service)
        self.filePath.setGeometry(QtCore.QRect(10, 260, 361, 21))
        self.filePath.setReadOnly(True)
        self.filePath.setObjectName(_fromUtf8("filePath"))
        self.lblOutput = QtGui.QLabel(Service)
        self.lblOutput.setGeometry(QtCore.QRect(10, 230, 101, 31))
        self.lblOutput.setObjectName(_fromUtf8("lblOutput"))
        self.lblName = QtGui.QLabel(Service)
        self.lblName.setGeometry(QtCore.QRect(10, 30, 51, 31))
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.name = QtGui.QLineEdit(Service)
        self.name.setGeometry(QtCore.QRect(110, 40, 301, 21))
        self.name.setObjectName(_fromUtf8("name"))

        self.retranslateUi(Service)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Service.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Service.reject)
        QtCore.QMetaObject.connectSlotsByName(Service)

    def retranslateUi(self, Service):
        Service.setWindowTitle(_translate("Service", "Compotte", None))
        self.label.setText(_translate("Service", "Connection information", None))
        self.lblUrl.setToolTip(_translate("Service", "<html><head/><body><p>Portal URL (for example http://erra.ccss.cz):</p></body></html>", None))
        self.lblUrl.setText(_translate("Service", "URL", None))
        self.lblUsername.setText(_translate("Service", "Username", None))
        self.lblPassword.setText(_translate("Service", "Password", None))
        self.checkBox.setToolTip(_translate("Service", "<html><head/><body><p>Use CAS authentification system, otherwise BASIC authentification will be used.</p></body></html>", None))
        self.checkBox.setText(_translate("Service", "CAS Authentification", None))
        self.cmdBrowseComposition.setText(_translate("Service", "...", None))
        self.lblOutput.setText(_translate("Service", "Output folder", None))
        self.lblName.setToolTip(_translate("Service", "<html><head/><body><p>Portal URL (for example http://erra.ccss.cz):</p></body></html>", None))
        self.lblName.setText(_translate("Service", "Name", None))

