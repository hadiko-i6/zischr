# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirm.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1007, 677)
        Form.setStyleSheet("background-color: rgb(46, 52, 54);\n"
"color: rgb(238, 238, 236);\n"
"font-size: 40px;")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.confirmLabel = QtWidgets.QLabel(Form)
        self.confirmLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.confirmLabel.setObjectName("confirmLabel")
        self.gridLayout.addWidget(self.confirmLabel, 2, 1, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.No = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.No.sizePolicy().hasHeightForWidth())
        self.No.setSizePolicy(sizePolicy)
        self.No.setMinimumSize(QtCore.QSize(300, 100))
        self.No.setStyleSheet("background-color: rgb(100, 19, 19);")
        self.No.setObjectName("No")
        self.gridLayout.addWidget(self.No, 5, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 5, 4, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 120, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 8, 2, 1, 1)
        self.Yes = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Yes.sizePolicy().hasHeightForWidth())
        self.Yes.setSizePolicy(sizePolicy)
        self.Yes.setMinimumSize(QtCore.QSize(300, 100))
        self.Yes.setStyleSheet("background-color: rgb(18, 88, 35);")
        self.Yes.setObjectName("Yes")
        self.gridLayout.addWidget(self.Yes, 5, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 4, 2, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 5, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem5, 1, 1, 1, 1)
        self.nagLabel = QtWidgets.QLabel(Form)
        self.nagLabel.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.478022, y1:0, x2:0.516, y2:1, stop:0 rgba(164, 0, 0, 255), stop:1 rgba(137, 0, 0, 255));\n"
"")
        self.nagLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.nagLabel.setObjectName("nagLabel")
        self.gridLayout.addWidget(self.nagLabel, 7, 1, 1, 3)
        spacerItem6 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem6, 6, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.confirmLabel.setText(_translate("Form", "Are you: NAME HERE ?"))
        self.No.setText(_translate("Form", "No"))
        self.Yes.setText(_translate("Form", "Yes"))
        self.nagLabel.setText(_translate("Form", ">>>  PAY YOUR DEBTS  <<<"))

