from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt


# pyright: reportAttributeAccessIssue=false

class HelpView(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("views_ui/help_view.ui", self)

        self.setWindowTitle("MFA Simulator Helper")
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.show()