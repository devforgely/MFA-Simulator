from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt

# pyright: reportAttributeAccessIssue=false

class HelpViewModel(QMainWindow):
    def __init__(self) -> None:
        QMainWindow.__init__(self)
        uic.loadUi("views/help_view.ui", self)

        self.setWindowTitle("MFA Simulator Helper")
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.show()
  