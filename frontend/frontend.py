#!/bin/python3

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidgetItem, QHeaderView, QTableWidget, QSpacerItem, QSizePolicy, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QResizeEvent, QBrush, QColor

from frontendgui import Ui_MainWindow
import cashingui
import confirmgui
import math

import grpc
import main_pb2
import main_pb2_grpc


# Uncomment when developing to show exceptions :)
#def customexcepthook(type, value, traceback):
#    print(traceback.print_exc(), file=sys.stderr)
#    sys.exit(1)
#sys.excepthook = customexcepthook


class i6CashInWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(i6CashInWidget, self).__init__(*args, **kwargs)

        self.ui = cashingui.Ui_Form()
        self.ui.setupUi(self)

        self.inputBuf = ""
        self.amount = 0
        self.ui.AmountLabel.setText("%.2f" % (self.amount / 100))

        def entry(a):
            self.inputBuf += a
            self.amount = int(self.inputBuf)
            self.ui.AmountLabel.setText("%.2f" % (self.amount / 100))

        def clear():
            self.inputBuf = ""
            self.amount = 0
            self.ui.AmountLabel.setText("%.2f" % (self.amount / 100))

        def negate():
            self.amount = -self.amount
            self.inputBuf = str(self.amount)
            self.ui.AmountLabel.setText("%.2f" % (self.amount / 100))

        self.doneCB = None  # Must be set on init

        self.ui.num0.clicked.connect(lambda x: entry("0"))
        self.ui.num1.clicked.connect(lambda x: entry("1"))
        self.ui.num2.clicked.connect(lambda x: entry("2"))
        self.ui.num3.clicked.connect(lambda x: entry("3"))
        self.ui.num4.clicked.connect(lambda x: entry("4"))
        self.ui.num5.clicked.connect(lambda x: entry("5"))
        self.ui.num6.clicked.connect(lambda x: entry("6"))
        self.ui.num7.clicked.connect(lambda x: entry("7"))
        self.ui.num8.clicked.connect(lambda x: entry("8"))
        self.ui.num9.clicked.connect(lambda x: entry("9"))
        self.ui.Clear.clicked.connect(clear)
        self.ui.Ok.clicked.connect(lambda x: self.doneCB(self.amount))
        self.ui.Cancel.clicked.connect(lambda x: self.doneCB(None))
        self.ui.Negate.clicked.connect(negate)

class i6ConfirmWidget(QWidget):
    def __init__(self, name, nag, *args, **kwargs):
        super(i6ConfirmWidget, self).__init__(*args, **kwargs)

        self.ui = confirmgui.Ui_Form()
        self.ui.setupUi(self)

        self.ui.confirmLabel.setText("Are you: %s ?" % name)

        self.doneCB = None

        self.ui.Yes.clicked.connect(lambda x: self.doneCB(True))
        self.ui.No.clicked.connect(lambda x: self.doneCB(False))

        if nag:
            self.nagTimer = QTimer()
            self.nagTimer.timeout.connect(self.toggleNag)
            self.nagTimer.start(400)
            self.nagCounter = 0
        else:
            self.ui.nagLabel.setText("")
            self.ui.nagLabel.setStyleSheet("")

    def toggleNag(self, *args):
        if self.nagCounter == 0:
            self.ui.nagLabel.setText(">>> PAY YOUR DEBTS <<<")
        elif self.nagCounter == 1:
            self.ui.nagLabel.setText(">>>  PAY YOUR DEBTS  <<<")
        elif self.nagCounter == 2:
            self.ui.nagLabel.setText(">>>   PAY YOUR DEBTS   <<<")
        elif self.nagCounter == 3:
            self.ui.nagLabel.setText(">>>  PAY YOUR DEBTS  <<<")

        self.nagCounter = (self.nagCounter + 1) % 4


class i6MainWindow(QMainWindow):
    def __init__(self, terminalId, channelUrl, biminame, *args, **kwargs):
        super(i6MainWindow, self).__init__(*args, **kwargs)
        self.biminame = biminame

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
        self.sortedAccounts = []

        self.channel = grpc.insecure_channel(channelUrl)
        self.backendStub = main_pb2_grpc.TerminalBackendStub(self.channel)

        self.buttons = []
        self.spacer = None  # Spacer for formatting buttons

        self.prevUUID = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerCB)
        self.timer.start(100)

        self.ui.cancelButton.clicked.connect(self.CancelButtonPressed)

        self.mainWidget = self.ui.mainWidgetStack.widget(0)
        self.cashinOpen = False
        self.cashinWidget = None

        self.confirmOpen = False
        self.confirmWidget = None

        self.updateButtons()
        self.updateOrdersList()
        self.updateAccountsList()

    def timerCB(self, *args):
        self.pollState()

        self.checkCashin()

        if not self.cashinOpen:
            self.sortAccounts()

            self.updateButtons()
            self.updateOrdersList()
            self.updateAccountsList()

            self.prevUUID = self.state.UUID

    def pollState(self):
        try:
            request = main_pb2.TerminalStateRequest()
            request.TerminalID = self.terminalId
            self.state = self.backendStub.GetState(request)
            self.setStatusbarError(self.state.LastScanError, False)
        except Exception as e:
            print(e)
            raise

    def sortAccounts(self):
        accounts = list(self.state.Accounts)
        self.sortedAccounts = sorted(accounts, key=lambda x: x.SortKey)

    def checkCashin(self):
        if not self.cashinOpen:
            if self.state.CashInScanReceived:
                self.cashinWidget = i6CashInWidget()
                self.cashinWidget.doneCB = self.cashinDone
                self.ui.mainWidgetStack.insertWidget(1, self.cashinWidget)
                self.ui.mainWidgetStack.setCurrentWidget(self.cashinWidget)
                self.cashinOpen = True

    def cashinDone(self, amount):
        self.cashinOpen = False
        self.ui.mainWidgetStack.setCurrentWidget(self.mainWidget)
        self.ui.mainWidgetStack.removeWidget(self.cashinWidget)
        del self.cashinWidget

        if amount is not None:
            request = main_pb2.TerminalAddDepositOrderRequest()
            request.TerminalID = self.terminalId
            request.CashInAmount = amount

            try:
                response = self.backendStub.AddDepositOrder(request)
                self.setStatusbarError(response.Error)
            except Exception as e:
                print(e)
                raise
        else:
            self.CancelButtonPressed()

    def updateButtons(self):
        if self.prevUUID == self.state.UUID:    # Current button state is equal to previous, no need to update
            return

        # Delete old buttons
        for button in self.buttons:
            self.ui.buttonContainer.widget().layout().removeWidget(button)
            button.deleteLater()
        if self.spacer is not None:
            self.ui.buttonContainer.widget().layout().removeItem(self.spacer)

        self.buttons = []

        i = 0
        for i in range(len(self.sortedAccounts)):
            account = self.sortedAccounts[i]
            newButton = QPushButton(account.DisplayName)
            newButton.userid = account.ID   # Append backend userid to button so we know who to bill if button is pressed
            newButton.userBalance = account.Balance
            newButton.setStyleSheet("color: rgb(238, 238, 236);")
            newButton.setMinimumHeight(60)
            self.ui.buttonContainer.widget().layout().addWidget(newButton, math.floor(i/2), i % 2)     # Add buttons in zig-zag pattern

            self.buttons.append(newButton)

            newButton.clicked.connect(self.NameButtonPressed)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.buttonContainer.widget().layout().addItem(self.spacer, math.floor(i / 2) + 1, 0)

        self.lastAccounts = list(self.sortedAccounts)

    def updateOrdersList(self):
        if self.prevUUID == self.state.UUID:    # Current button state is equal to previous, no need to update
            return

        self.NameButtonPressedConfirmationCB(False)     # In case somebody scanned in drink during confirm dialog, cancel!

        self.ui.currentOrderList.clear()

        self.ui.currentOrderList.setColumnCount(2)
        self.ui.currentOrderList.setRowCount(len(self.state.PendingOrders))

        self.ui.currentOrderList.setHorizontalHeaderLabels(["Name", "Price"])

        for i in range(len(self.state.PendingOrders)):
            order = self.state.PendingOrders[i]
            if order.NeedsReview:
                nameWidget = QTableWidgetItem("Talk to %s: %s" % (self.biminame, order.DisplayName))
                nameWidget.setBackground(QBrush(QColor(120, 84, 0)))
            else:
                nameWidget = QTableWidgetItem(order.DisplayName)
            self.ui.currentOrderList.setItem(i, 0, nameWidget)

            if order.NeedsReview:
                priceWdiget = QTableWidgetItem("?.??€")
                priceWdiget.setBackground(QBrush(QColor(120, 84, 0)))
            else:
                priceWdiget = QTableWidgetItem("%.2f€" % (order.Price / 100))
            priceWdiget.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.currentOrderList.setItem(i, 1, priceWdiget)

        self.lastOrders = list(self.state.PendingOrders)

        self.ui.totalAmountLabel.setText("%.2f€" % (self.state.PendingOrdersTotal / 100))

    def updateAccountsList(self):
        if self.prevUUID == self.state.UUID:
            return

        self.ui.accountsList.clear()

        self.ui.accountsList.setColumnCount(4)
        self.ui.accountsList.setRowCount(math.ceil(len(self.sortedAccounts)/2))

        self.ui.accountsList.setHorizontalHeaderLabels(["Name", "Balance"]*2)

        for i in range(len(self.sortedAccounts)):
            if i % 2 == 0:
                columnoffset = 0
            else:
                columnoffset = 2

            account = self.sortedAccounts[i]
            nameWidget = QTableWidgetItem(account.DisplayName)
            self.ui.accountsList.setItem(math.floor(i / 2), 0 + columnoffset, nameWidget)

            balanceWidget = QTableWidgetItem("%.2f€" % (account.Balance / 100))
            balanceWidget.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.accountsList.setItem(math.floor(i / 2), 1 + columnoffset, balanceWidget)


    def NameButtonPressed(self, *args):
        clickedButton = self.sender()    # WTF why isn't this passed as argument?
        userID = clickedButton.userid
        userBalance = clickedButton.userBalance

        self.confirmWidget = i6ConfirmWidget(clickedButton.text(), userBalance < 0)
        self.confirmWidget.doneCB = self.NameButtonPressedConfirmationCB
        self.confirmWidget.userID = userID
        self.ui.mainWidgetStack.insertWidget(1, self.confirmWidget)
        self.ui.mainWidgetStack.setCurrentWidget(self.confirmWidget)
        self.confirmOpen = True

    def NameButtonPressedConfirmationCB(self, ack):
        if ack:
            request = main_pb2.TerminalBuyRequest()
            request.TerminalID = self.terminalId
            request.AccountID = self.confirmWidget.userID
            request.UUID = self.state.UUID
            try:
                pass
                response = self.backendStub.Buy(request)
                self.setStatusbarError(response.Error)

            except Exception as e:
                print(e)
                raise
        if self.confirmOpen:
            self.ui.mainWidgetStack.setCurrentWidget(self.mainWidget)
            self.ui.mainWidgetStack.removeWidget(self.confirmWidget)
            self.confirmOpen = False

    def CancelButtonPressed(self):
        request = main_pb2.AbortRequest()
        request.TerminalID = self.terminalId

        try:
            pass
            response = self.backendStub.Abort(request)
            self.setStatusbarError(response.Error)
        except Exception as e:
            print(e)
            raise

    def setStatusbarError(self, message, clearIfEmpty=True):
        if message:
            self.ui.statusbar.showMessage(message)
            print(message)
            self.ui.statusbar.setStyleSheet("background-color: rgb(100, 19, 19);")
        elif clearIfEmpty:
            self.ui.statusbar.clearMessage()
            self.ui.statusbar.setStyleSheet("")

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

        orderlistSize = self.ui.currentOrderList.maximumViewportSize()
        self.ui.totalAmountLabel.setFixedWidth(0.2 * orderlistSize.width())

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--id', help='Terminal ID', default="Foo")
    parser.add_argument('--backendurl', help='URL to backend', default="localhost:8080")
    parser.add_argument('--windowed', help='Fullscreen mode', default=True, action="store_true")
    parser.add_argument('--bimi', help='Name of the guy administrating everything', default="Bimi")
    parser.add_argument('--winwidth', help='Window width (also works for fullscreen)', default=1024, type=int)
    parser.add_argument('--winheight', help='Window height(also works for fullscreen)', default=768, type=int)

    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = i6MainWindow(args.id, args.backendurl, args.bimi)

    if not args.windowed:
        window.showFullScreen()
    else:
        window.show()

    window.resize(args.winwidth, args.winheight)

    window.scaleTables()
    sys.exit(app.exec_())
