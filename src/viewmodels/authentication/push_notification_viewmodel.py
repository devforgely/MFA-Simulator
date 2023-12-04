from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
from viewmodels.authentication.authentication_base import *
import uuid
import random


class PushNotificationRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/register_views/push_notification_view.ui", self)
        self.setup_btn.clicked.connect(self.next)
        self.continue_btn.clicked.connect(self.next)
        self.scan_btn.clicked.connect(lambda: self.phone_container.setCurrentIndex(self.phone_container.currentIndex()+1))
        self.link_btn.clicked.connect(self.send)
        # self.cancel_btn.clicked.connect(self.cancel)

    def next(self) -> None:
        currentIndex = self.left_stacked.currentIndex()
        if currentIndex + 1 < self.left_stacked.count():
            self.left_stacked.setCurrentIndex(currentIndex + 1)
            if (currentIndex + 1 == self.left_stacked.count()):
                self.phone_container.setCurrentIndex(self.phone_container.currentIndex()+1)

    def send(self) -> None:
        device_id = str(uuid.uuid4())
        if self.authentication_service.register(device_id):
            self.authentication_service.session_store(device_id)
            self.message_service.send(self, "Registered", None)
            

class PushNotificationAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/authenticate_views/push_notification_view.ui", self) 

        self.verify_btn.clicked.connect(self.send)
        self.code_btn.clicked.connect(self.generate_code)

    def generate_code(self) -> None:
        otp = ''.join(str(random.randint(0, 9)) for _ in range(3))
        self.code_label.setText(otp)

    def send(self) -> None:
        device_id = self.authentication_service.get_session_stored()[0]
        if self.authentication_service.authenticate(device_id):
            if self.code_field.text() == self.code_label.text():
                self.message_service.send(self, "Authenticated", None)
            else:
                QMessageBox.warning(self, "Error", "Authentication failed. Try again.")