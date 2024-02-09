from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from services.container import ApplicationContainer


class ManageViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/manage_view.ui", self)