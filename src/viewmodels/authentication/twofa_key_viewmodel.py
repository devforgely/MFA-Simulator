from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QPushButton
from viewmodels.authentication.authentication_base import *
from widgets.waiting_spinner import QtWaitingSpinner
import uuid
import random


# pyright: reportGeneralTypeIssues=false

class TwoFAKeyRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/register_views/twofa_key_view.ui", self)
        
        self.next_btn = QPushButton('Next')
        self.next_btn.setMinimumWidth(100)
        self.next_btn.setMinimumHeight(35)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.page1.layout().addWidget(self.next_btn, alignment=Qt.AlignRight)
        w = QtWaitingSpinner(self.page1)
        self.page1.layout().addWidget(w)
        w.start()

        self.connect_btn.clicked.connect(self.send)
        self.on_btn.clicked.connect(self.send)

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