from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
from viewmodels.authentication.authentication_base import *
import uuid
import random


class TwoFAKeyRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/register_views/twofa_key_view.ui", self)
        
        self.link_btn.clicked.connect(self.send)

    def send(self) -> None:
        device_id = str(uuid.uuid4())
        if self.authentication_service.register(device_id):
            self.authentication_service.session_store(device_id)
            self.message_service.send(self, "Registered", None)
            

class TwoFAKeyAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/authenticate_views/twofa_key_view.ui", self) 

        self.plug_btn.clicked.connect(self.activiate_device)
        self.confirm_btn.clicked.connect(self.send)

    def activiate_device(self) -> None:
        otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
        self.code_label.setText(otp)

    def send(self) -> None:
        device_id = self.authentication_service.get_session_stored()[0]
        if self.authentication_service.authenticate(device_id):
            if self.code_field.text() == self.code_label.text():
                self.message_service.send(self, "Authenticated", None)
            else:
                QMessageBox.warning(self, "Error", "Authentication failed. Try again.")