from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from viewmodels.authentication.authentication_base import *
import random

class FingerPrintRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/fingerprint_view.ui", info_panel)
        
        self.progress = 0

        self.fingerprint_btn.clicked.connect(self.set_fingerprint)

    def set_fingerprint(self) -> None:
        if self.progress < 6:
            step = random.choice([1, 2])
            self.progress += step
            if self.progress >= 6:
                self.progress = 6
                self.instruction_label.setText("Registeration Completed")
                self.send()
            self.fingerprint_btn.setIcon(QIcon(QPixmap(f"resources/images/fp{self.progress}.png")))

    def send(self) -> None:
        if self.authentication_service.register('data/fingerprints/fp1.png'):
            self.message_service.send(self, "Registered", None)
            

class FingerPrintAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/fingerprint_view.ui", info_panel)

        self.fingerprint_btn.clicked.connect(self.send)

    def send(self) -> None:
        if random.random() < 0.4:
            QMessageBox.warning(self, "Error", "Authenticate fingerprint failed. Try again.")
        else:
            if self.authentication_service.authenticate('data/fingerprints/fp1.png'):
                self.message_service.send(self, "Authenticated", None)
            else:
                print("wrong key")