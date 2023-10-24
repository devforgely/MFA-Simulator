from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLineEdit
from services.container import ApplicationContainer

class PasswordRegisterViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        uic.loadUi("views/register_views/password_view.ui", self)   

        self.password_field.setEchoMode(QLineEdit.Password)
        self.submit_btn.clicked.connect(self.send)

    def send(self) -> None:
        print("sending...")
        plain_key = self.password_field.text()
        hashed_key = self.authentication_service.register(plain_key)
        if hashed_key != "":
            self.message_service.send(self, "Change View", None)
            

class PasswordAuthenticateViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        uic.loadUi("views/authenticate_views/password_view.ui", self) 

        self.password_field.setEchoMode(QLineEdit.Password)
        self.submit_btn.clicked.connect(self.send)

    def send(self) -> None:
        print("sending...")
        plain_key = self.password_field.text()
        truth = self.authentication_service.authenticate(plain_key)
        if truth == True:
            self.message_service.send(self, "Change View", None)
        else:
            print("wrong key")
            self.password_field.clear()