from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer

class AuthenticationBaseViewModel(QObject):
    state_change = pyqtSignal(str, int)
    state_data_change = pyqtSignal(dict, int)

    def __init__(self) -> None:
        super().__init__()
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()