from PyQt5.QtWidgets import QWidget
from services.container import ApplicationContainer

class AuthenticationBaseViewModel(QWidget):
    def __init__(self, info_panel: QWidget) -> None:
        QWidget.__init__(self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()
        self.info_panel = info_panel

    def send(self) -> None:
        ...