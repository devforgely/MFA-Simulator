from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from services.container import ApplicationContainer

class AuthenticationBaseViewModel(QWidget):
    def __init__(self, ui: str, info_panel: QWidget) -> None:
        QWidget.__init__(self)
        uic.loadUi(ui, self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()
        self.info_panel = info_panel

    def initalise_infopanel(self) -> None:
        ...

    def send(self) -> None:
        ...