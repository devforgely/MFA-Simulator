from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
from viewmodels.authentication.authentication_base import *
import random

# pyright: reportGeneralTypeIssues=false

class FingerPrintRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/register_views/fingerprint_view.ui", self)
        
        self.fp_layout.setAlignment(Qt.AlignHCenter)
        self.fingerprint_btn.clicked.connect(self.send)

    def send(self) -> None:
        if random.random() < 0.4:
            QMessageBox.warning(self, "Error", "Register fingerprint failed. Try again.")
        else:
            if self.authentication_service.register('data/fingerprints/fp1.png'):
                self.message_service.send(self, "Registered", None)
            

class FingerPrintAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/authenticate_views/fingerprint_view.ui", self) 

        self.fp_layout.setAlignment(Qt.AlignHCenter)
        self.fingerprint_btn.clicked.connect(self.send)

    def send(self) -> None:
        if self.authentication_service.authenticate('data/fingerprints/fp1.png'):
            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")