# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import src_rc

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(276, 138)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/q/src/电视粉.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        About.setWindowIcon(icon)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(10)
        self.groupBox = QtWidgets.QGroupBox(About)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 241, 121))
        self.groupBox.setObjectName("groupBox")
        self.info = QtWidgets.QLabel(self.groupBox)
        self.info.setFont(font)
        self.info.setStyleSheet("color: rgb(255, 69, 240);")
        self.info.setGeometry(QtCore.QRect(30, 30, 233, 70))
        self.info.setObjectName("info")
        self.gridFrame = QtWidgets.QFrame(About)
        self.gridFrame.setGeometry(QtCore.QRect(20, 10, 241, 121))
        self.gridFrame.setObjectName("gridFrame")
        self.gridFrame.setStyleSheet("background-image: url(:/q/src/about.png);")
        self.gridFrame.lower()

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About"))
        self.groupBox.setTitle(_translate("About", "关于"))
        self.info.setText(_translate("About", "blbldl v1.0.1 \nbuild 20210810\nmade by xy\ncontact:\nxyseer2@gmail.com"))
