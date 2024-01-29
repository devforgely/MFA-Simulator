from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from services.container import ApplicationContainer


class ProfileViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/profile_view.ui", self)