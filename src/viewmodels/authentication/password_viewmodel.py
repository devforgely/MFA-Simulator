from PyQt5 import uic
from PyQt5.QtWidgets import QLineEdit
from viewmodels.authentication.authentication_base import *

class PasswordRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/register_views/password_view.ui", self)   

        self.password_field.setEchoMode(QLineEdit.Password)
        self.repassword_field.setEchoMode(QLineEdit.Password)
        self.submit_btn.clicked.connect(self.send)

    def send(self) -> None:
        if self.password_field.text() == self.repassword_field.text():
            if self.authentication_service.register(self.username_field.text() + ";" + self.password_field.text()):
                self.plain_key_label.setText(self.authentication_service.get_plain_key())
                self.hashed_key_label.setText(self.authentication_service.get_secret())
                self.timestamp_label.setText(self.authentication_service.get_timestamp())
                self.message_service.send(self, "Registered", None)
            

class PasswordAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/authenticate_views/password_view.ui", self) 

        self.password_field.setEchoMode(QLineEdit.Password)
        self.submit_btn.clicked.connect(self.send)

    def send(self) -> None:
        truth = self.authentication_service.authenticate(self.username_field.text() + ";" + self.password_field.text())
        if truth == True:
            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")
            self.password_field.clear()