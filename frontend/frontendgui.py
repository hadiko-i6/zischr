# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frontend.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(982, 735)
        MainWindow.setStyleSheet("background-color: rgb(46, 52, 54);\n"
"color: rgb(238, 238, 236);\n"
"font-size: 20px;\n"
"alternate-background-color: rgb(56, 63, 67);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.currentOrderList = QtWidgets.QTableWidget(self.frame)
        self.currentOrderList.setStyleSheet("")
        self.currentOrderList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.currentOrderList.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.currentOrderList.setAlternatingRowColors(True)
        self.currentOrderList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.currentOrderList.setObjectName("currentOrderList")
        self.currentOrderList.setColumnCount(2)
        self.currentOrderList.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.currentOrderList.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.currentOrderList.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.currentOrderList.setHorizontalHeaderItem(1, item)
        self.currentOrderList.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.currentOrderList)
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setStyleSheet("background-color: rgb(100, 19, 19);\n"
"")
        self.cancelButton.setObjectName("cancelButton")
        self.verticalLayout.addWidget(self.cancelButton)
        self.accountsList = QtWidgets.QTableWidget(self.frame)
        self.accountsList.setStyleSheet("font-size: 12px;")
        self.accountsList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.accountsList.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.accountsList.setAlternatingRowColors(True)
        self.accountsList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.accountsList.setGridStyle(QtCore.Qt.SolidLine)
        self.accountsList.setRowCount(3)
        self.accountsList.setObjectName("accountsList")
        self.accountsList.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.accountsList.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.accountsList.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.accountsList.setHorizontalHeaderItem(1, item)
        self.accountsList.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.accountsList)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.buttonContainer = QtWidgets.QScrollArea(self.centralwidget)
        self.buttonContainer.setWidgetResizable(True)
        self.buttonContainer.setObjectName("buttonContainer")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 477, 683))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.buttonContainer.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.buttonContainer, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        item = self.currentOrderList.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "New Row"))
        item = self.currentOrderList.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.currentOrderList.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Price"))
        self.cancelButton.setText(_translate("MainWindow", "Cancel Order"))
        item = self.accountsList.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "New Row"))
        item = self.accountsList.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.accountsList.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Balance"))

