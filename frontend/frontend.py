#!/bin/python3

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidgetItem, QHeaderView, QAbstractItemView, QTableWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QResizeEvent

from frontendgui import Ui_MainWindow
import math

import grpc
import main_pb2
import main_pb2_grpc

class ProgramState():
    class orderEntry:
        def __init__(self):
            self.DisplayName = "N/A"
            self.UnitPrice = 0.0

    class accountEntry:
        def __init__(self):
            self.ID = ""
            self.DisplayName = "Max Mustermann"
            self.Balance = 0.0

    def __init__(self):
        self.OrderList = []
        self.Accounts = []

class i6MainWindow(QMainWindow):
    def __init__(self, terminalId, *args, **kwargs):
        super(i6MainWindow, self).__init__(*args, **kwargs)

        self.terminalId = terminalId

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.currentOrderList.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.currentOrderList.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.currentOrderList.setSelectionMode(QTableWidget.NoSelection)
        self.ui.accountsList.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.state = main_pb2.TerminalStateResponse()
        #self.state.buttonList = ["goo", "bar", "Joe", "Luke", "Christian", "Flurgeist", "Dreckige Toilette"]    # TEMP DEV LINE TODO: REMOVE
        s1 = main_pb2.TerminalStateResponse.Order()
        s1.DisplayName = "Holi aber echt langer name lolololo  asdasdfasdfgkj"
        s1.UnitPrice = int(85)
        self.state.OrderList.extend([
            s1,
            s1,
            s1
        ])

        a1 = main_pb2.TerminalStateResponse.Account()
        a1.ID = "fuck"
        a1.DisplayName = "Dein Gesicht"
        a1.Balance = 1234
        self.state.Accounts.extend([a1])

        self.channel = grpc.insecure_channel('localhost:50051')
        self.backendStub = main_pb2_grpc.TerminalBackendStub(self.channel)

        self.buttons = []
        self.lastAccounts = []    # Stores the last list of button names to be updated

        self.updateButtons()
        self.updateOrdersList()
        self.updateAccountsList()

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerCB)
        self.timer.start(1000)

    def timerCB(self, *args):
        self.pollState()

        self.updateButtons()
        self.updateOrdersList()
        self.updateAccountsList()

    def pollState(self):
        try:
            request = main_pb2.TerminalStateRequest()
            request.TerminalID = self.terminalId
            #self.state = self.backendStub.GetState(request)
        except Exception as e:
            print(e)


    def updateButtons(self):
        if self.lastAccounts == list(self.state.Accounts):    # Current button state is equal to previous, no need to update
            return

        # Delete old buttons
        for button in self.buttons:
            self.ui.buttonContainer.widget().layout().removeWidget(button)
            button.deleteLater()

        self.buttons = []

        for i in range(len(self.state.Accounts)):
            account = self.state.Accounts[i]
            newButton = QPushButton(account.DisplayName)
            newButton.userid = account.ID   # Append backend userid to button so we know who to bill if button is pressed
            newButton.setStyleSheet("color: rgb(238, 238, 236);")
            self.ui.buttonContainer.widget().layout().addWidget(newButton, math.floor(i/2), i % 2)     # Add buttons in zig-zag pattern

            self.buttons.append(newButton)

            newButton.clicked.connect(self.NameButtonPressed)

        self.lastAccounts = list(self.state.Accounts)

    def updateOrdersList(self):
        self.ui.currentOrderList.clear()

        self.ui.currentOrderList.setColumnCount(2)
        self.ui.currentOrderList.setRowCount(len(self.state.OrderList))

        self.ui.currentOrderList.setHorizontalHeaderLabels(["Name", "Price"])

        for i in range(len(self.state.OrderList)):
            order = self.state.OrderList[i]
            nameWidget = QTableWidgetItem(order.DisplayName)
            self.ui.currentOrderList.setItem(i, 0, nameWidget)

            priceWdiget = QTableWidgetItem("€%.2f" % (order.UnitPrice / 100))
            priceWdiget.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.currentOrderList.setItem(i, 1, priceWdiget)

        # TODO: Totals Entry at bottom

    def updateAccountsList(self):
        self.ui.accountsList.clear()

        self.ui.accountsList.setColumnCount(2)
        self.ui.accountsList.setRowCount(len(self.state.Accounts))

        self.ui.accountsList.setHorizontalHeaderLabels(["Name", "Balance"])

        for i in range(len(self.state.Accounts)):
            account = self.state.Accounts[i]
            nameWidget = QTableWidgetItem(account.DisplayName)
            self.ui.accountsList.setItem(i, 0, nameWidget)

            balanceWidget = QTableWidgetItem("€%.2f" % (account.Balance / 100))
            balanceWidget.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.accountsList.setItem(i, 1, balanceWidget)


    def NameButtonPressed(self, *args):
        clickedButton = self.sender()    # WTF why isn't this passed as argument?
        clickedIndex = self.buttons.index(clickedButton)
        print("Clicked: %s %s (%s)" % (clickedIndex, clickedButton.text(), clickedButton.userid))

        # TODO: Confirmation dialog

        request = main_pb2.TerminalBuyRequest()
        request.TerminalID = self.terminalId
        request.AccountID = clickedButton.userid
        try:
            pass
            #response = self.backendStub.Buy(request)
        except Exception as e:
            print(e)

        # TODO: Display returned error as modal dialog

    def resizeEvent(self, a0: QResizeEvent):
        self.scaleTables()

    def scaleTables(self):
        orderlistSize = self.ui.currentOrderList.maximumViewportSize()
        self.ui.currentOrderList.setColumnWidth(0, 0.8 * orderlistSize.width())
        self.ui.currentOrderList.setColumnWidth(1, 0.2 * orderlistSize.width())

        accountlistSize = self.ui.accountsList.maximumViewportSize()
        self.ui.accountsList.setColumnWidth(0, 0.8 * accountlistSize.width())
        self.ui.accountsList.setColumnWidth(1, 0.2 * accountlistSize.width())


app = QApplication(sys.argv)
window = i6MainWindow("Foo")

window.show()
window.scaleTables()
sys.exit(app.exec_())