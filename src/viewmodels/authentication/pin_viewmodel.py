from PyQt5 import uic
from PyQt5.QtWidgets import QLineEdit
from viewmodels.authentication.authentication_base import *

class PinRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/register_views/pin_view.ui", self)

        self.pin_field.setEchoMode(QLineEdit.Password)
        self.btn0.clicked.connect(lambda: self.update_field("0"))
        self.btn1.clicked.connect(lambda: self.update_field("1"))
        self.btn2.clicked.connect(lambda: self.update_field("2"))
        self.btn3.clicked.connect(lambda: self.update_field("3"))
        self.btn4.clicked.connect(lambda: self.update_field("4"))
        self.btn5.clicked.connect(lambda: self.update_field("5"))
        self.btn6.clicked.connect(lambda: self.update_field("6"))
        self.btn7.clicked.connect(lambda: self.update_field("7"))
        self.btn8.clicked.connect(lambda: self.update_field("8"))
        self.btn9.clicked.connect(lambda: self.update_field("9"))
        self.clear_btn.clicked.connect(lambda: self.update_field("$"))
        self.submit_btn.clicked.connect(lambda: self.send())

    def update_field(self, char: str) -> None:
        if char == "$":
            self.pin_field.setText("")
        else:
            self.pin_field.setText(self.pin_field.text()+char)

    def send(self) -> None:
        plain_key = self.pin_field.text()

        if len(plain_key) < 3: return

        if self.authentication_service.register(plain_key):
            self.message_service.send(self, "Registered", None)  


class PinAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        uic.loadUi("views/authenticate_views/pin_view.ui", self)

        self.pin_field.setEchoMode(QLineEdit.Password)
        self.btn0.clicked.connect(lambda: self.update_field("0"))
        self.btn1.clicked.connect(lambda: self.update_field("1"))
        self.btn2.clicked.connect(lambda: self.update_field("2"))
        self.btn3.clicked.connect(lambda: self.update_field("3"))
        self.btn4.clicked.connect(lambda: self.update_field("4"))
        self.btn5.clicked.connect(lambda: self.update_field("5"))
        self.btn6.clicked.connect(lambda: self.update_field("6"))
        self.btn7.clicked.connect(lambda: self.update_field("7"))
        self.btn8.clicked.connect(lambda: self.update_field("8"))
        self.btn9.clicked.connect(lambda: self.update_field("9"))
        self.clear_btn.clicked.connect(lambda: self.update_field("$"))
        self.submit_btn.clicked.connect(lambda: self.send())

    def update_field(self, char: str) -> None:
        if char == "$":
            self.pin_field.setText("")
        else:
            self.pin_field.setText(self.pin_field.text()+char)

    def send(self) -> None:
        plain_key = self.pin_field.text()

        truth = self.authentication_service.authenticate(plain_key)
        if truth == True:
            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")
            self.pin_field.clear()
