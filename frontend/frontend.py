#!/bin/python3

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidgetItem
from PyQt5.QtCore import QTimer

from frontendgui import Ui_MainWindow

import math

class ProgramState():
    class orderEntry:
        def __init__(self):
            self.name = "N/A"
            self.price = 0.0
            self.amount = 0

    class accountsEntry:
        def __init__(self):
            self.name = "Max Mustermann"
            self.balance = 0.0

    def __init__(self):
        self.orderList = []
        self.accountList = []
        self.buttonList = []

    def pollState(self):
        print("'polling'")

class i6MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(i6MainWindow, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.state = ProgramState()
        self.state.pollState()
        self.state.buttonList = ["goo", "bar", "Joe", "Luke", "Christian", "Flurgeist", "Dreckige Toilette"]    # TEMP DEV LINE TODO: REMOVE
        s1 = ProgramState.orderEntry()
        s1.name = "HoLi"
        s1.amount = 10
        s1.price = 0.85
        self.state.orderList = [
            s1,
            s1,
            s1
        ]

        self.buttons = []
        self.lastButtonList = []    # Stores the last list of button names to be updated

        self.updateButtons()
        self.updateOrdersList()

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerCB)
        self.timer.start(1000)

    def timerCB(self, *args):
        self.state.pollState()
        self.updateButtons()
        #self.updateOrdersList
        #self.updateAccountsList

    def updateButtons(self):
        if self.state.buttonList == self.lastButtonList:    # Current button state is equal to previous, no need to update
            return

        for button in self.buttons:     # Delete old buttons
            self.ui.buttonContainer.widget().layout().removeWidget(button)
            button.deleteLater()

        self.buttons = []

        for i in range(len(self.state.buttonList)):
            name = self.state.buttonList[i]
            newButton = QPushButton(name)
            self.ui.buttonContainer.widget().layout().addWidget(newButton, math.floor(i/2), i % 2)     # Add buttons in zig-zag pattern

            self.buttons.append(newButton)

            newButton.clicked.connect(self.NameButtonPressed)

    def updateOrdersList(self):
        self.ui.currentOrderList.clear()

        self.ui.currentOrderList.setColumnCount(4)
        self.ui.currentOrderList.setRowCount(len(self.state.orderList))

        for i in range(len(self.state.orderList)):
            order = self.state.orderList[i]
            nameWidget = QTableWidgetItem(order.name)
            self.ui.currentOrderList.setItem(i, 0, nameWidget)
            amountWidget = QTableWidgetItem("%.2f" % order.amount)
            self.ui.currentOrderList.setItem(i, 1, amountWidget)
            priceWdiget = QTableWidgetItem("%.2f" % order.price)
            self.ui.currentOrderList.setItem(i, 2, priceWdiget)
            totalWidget = QTableWidgetItem("%.2f" % (order.price * order.amount))
            self.ui.currentOrderList.setItem(i, 3, totalWidget)

    def NameButtonPressed(self, *args):
        clickedButton = self.sender()    # WTF why isn't this passed as argument?
        clickedIndex = self.buttons.index(clickedButton)
        print("Clicked: %s %s" % (clickedIndex, clickedButton.text()))

        # TODO: RPC call to backend to let it know that button i was clicked





app = QApplication(sys.argv)
window = i6MainWindow()

window.show()
sys.exit(app.exec_())