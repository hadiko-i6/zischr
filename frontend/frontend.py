import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from frontend.frontendgui import Ui_MainWindow


class ProgramState():
    pass

class i6MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(i6MainWindow, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.buttons = []

    def updateButtons(self):
        clickableNames = ["goo", "bar", "Joe", "Luke", "Christian", "Flurgeist", "Dreckige Toilette"]

        for i in range(len(clickableNames)):
            name = clickableNames[i]
            newButton = QPushButton(name)
            self.ui.buttonContainer.layout().addWidget(newButton, ())
            newButton.clicked.connect(lambda x: self.NameButtonPressed)

    def NameButtonPressed(self, index):
        pass





app = QApplication(sys.argv)
window = QMainWindow()

window.show()
sys.exit(app.exec_())