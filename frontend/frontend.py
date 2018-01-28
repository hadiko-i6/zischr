#!/bin/python3

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidgetItem, QHeaderView, QTableWidget, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QResizeEvent

from frontendgui import Ui_MainWindow
import math

import grpc
import main_pb2
import main_pb2_grpc


def customexcepthook(type, value, traceback):
    print(traceback.print_exc(), file=sys.stderr)
    sys.exit(1)
#sys.excepthook = customexcepthook


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

        self.ui.currentOrderList.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.accountsList.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.currentOrderList.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.currentOrderList.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.accountsList.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.accountsList.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.state = main_pb2.TerminalStateResponse()

        self.channel = grpc.insecure_channel('localhost:8080')  # TODO: set as arg
        self.backendStub = main_pb2_grpc.TerminalBackendStub(self.channel)

        self.buttons = []
        self.lastAccounts = []    # Stores the last list of button names to be updated
        self.spacer = None  # Spacer for formatting buttons

        self.updateButtons()
        self.updateOrdersList()
        self.updateAccountsList()

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerCB)
        self.timer.start(100)

        self.ui.cancelButton.clicked.connect(self.CancelButtonPressed)

    def timerCB(self, *args):
        self.pollState()

        self.updateButtons()
        self.updateOrdersList()
        self.updateAccountsList()

    def pollState(self):
        try:
            request = main_pb2.TerminalStateRequest()
            request.TerminalID = self.terminalId
            self.state = self.backendStub.GetState(request)
        except Exception as e:
            print(e)
            raise


    def updateButtons(self):
        if self.lastAccounts == list(self.state.Accounts):    # Current button state is equal to previous, no need to update
            return

        # Delete old buttons
        for button in self.buttons:
            self.ui.buttonContainer.widget().layout().removeWidget(button)
            button.deleteLater()
        if self.spacer is not None:
            self.ui.buttonContainer.widget().layout().removeItem(self.spacer)

        self.buttons = []

        for i in range(len(self.state.Accounts)):
            account = self.state.Accounts[i]
            newButton = QPushButton(account.DisplayName)
            newButton.userid = account.ID   # Append backend userid to button so we know who to bill if button is pressed
            newButton.setStyleSheet("color: rgb(238, 238, 236);")
            newButton.setMinimumHeight(60)
            self.ui.buttonContainer.widget().layout().addWidget(newButton, math.floor(i/2), i % 2)     # Add buttons in zig-zag pattern

            self.buttons.append(newButton)

            newButton.clicked.connect(self.NameButtonPressed)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.buttonContainer.widget().layout().addItem(self.spacer, math.floor(i / 2) + 1, 0)

        self.lastAccounts = list(self.state.Accounts)

    def updateOrdersList(self):
        self.ui.currentOrderList.clear()

        self.ui.currentOrderList.setColumnCount(2)
        self.ui.currentOrderList.setRowCount(len(self.state.PendingOrders))

        self.ui.currentOrderList.setHorizontalHeaderLabels(["Name", "Price"])

        for i in range(len(self.state.PendingOrders)):
            order = self.state.PendingOrders[i]
            nameWidget = QTableWidgetItem(order.DisplayName)
            self.ui.currentOrderList.setItem(i, 0, nameWidget)

            priceWdiget = QTableWidgetItem("€%.2f" % (order.Price / 100))
            priceWdiget.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.currentOrderList.setItem(i, 1, priceWdiget)

        # TODO: Totals Entry at bottom

    def updateAccountsList(self):
        self.ui.accountsList.clear()

        self.ui.accountsList.setColumnCount(4)
        self.ui.accountsList.setRowCount(math.ceil(len(self.state.Accounts)/2))

        self.ui.accountsList.setHorizontalHeaderLabels(["Name", "Balance"]*2)

        for i in range(len(self.state.Accounts)):
            if i % 2 == 0:
                columnoffset = 0
            else:
                columnoffset = 2

            account = self.state.Accounts[i]
            nameWidget = QTableWidgetItem(account.DisplayName)
            self.ui.accountsList.setItem(math.floor(i / 2), 0 + columnoffset, nameWidget)

            balanceWidget = QTableWidgetItem("€%.2f" % (account.Balance / 100))
            balanceWidget.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.accountsList.setItem(math.floor(i / 2), 1 + columnoffset, balanceWidget)


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
            response = self.backendStub.Buy(request)
        except Exception as e:
            print(e)
            raise

        # TODO: Display returned error as modal dialog

    def CancelButtonPressed(self):
        request = main_pb2.AbortRequest()
        request.TerminalID = self.terminalId

        try:
            pass
            response = self.backendStub.Abort(request)
            print(response)
        except Exception as e:
            print(e)
            raise


    def resizeEvent(self, a0: QResizeEvent):
        self.scaleTables()

    def scaleTables(self):
        orderlistSize = self.ui.currentOrderList.maximumViewportSize()
        self.ui.currentOrderList.setColumnWidth(0, 0.8 * orderlistSize.width())
        self.ui.currentOrderList.setColumnWidth(1, 0.2 * orderlistSize.width())

        accountlistSize = self.ui.accountsList.maximumViewportSize()
        self.ui.accountsList.setColumnWidth(0, 0.35 * accountlistSize.width())
        self.ui.accountsList.setColumnWidth(1, 0.15 * accountlistSize.width())
        self.ui.accountsList.setColumnWidth(2, 0.35 * accountlistSize.width())
        self.ui.accountsList.setColumnWidth(3, 0.15 * accountlistSize.width())


app = QApplication(sys.argv)
window = i6MainWindow("Foo")

window.show()
window.scaleTables()
sys.exit(app.exec_())
