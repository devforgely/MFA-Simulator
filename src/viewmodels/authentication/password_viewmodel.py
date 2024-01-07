from PyQt5 import uic
from PyQt5.QtWidgets import QLineEdit
from viewmodels.authentication.authentication_base import *

class PasswordRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/register_views/password_view.ui", self)

        self.info_panel.add_client_data("username", "null")
        self.info_panel.add_client_data("password", "null")
        
        self.info_panel.add_server_data("user_registered", "null")
        self.info_panel.add_server_data("user_password", "null")

        self.info_panel.log_text("Waiting for username and password...")

        self.password_field.setEchoMode(QLineEdit.Password)
        self.repassword_field.setEchoMode(QLineEdit.Password)
        self.submit_btn.clicked.connect(self.send)

    def send(self) -> None:
        if self.password_field.text() == self.repassword_field.text():
            if self.authentication_service.register(self.username_field.text(), self.password_field.text()):
                self.info_panel.update_client_status("request", "registration")
                self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

                self.info_panel.update_server_status("status", "200")
                self.info_panel.update_server_status("message", "user registered")

                self.info_panel.update_client_data("username", self.username_field.text())
                self.info_panel.update_client_data("password", self.password_field.text())

                self.info_panel.update_server_data("user_registered", self.authentication_service.get_session_stored()["user_registered"])
                self.info_panel.update_server_data("user_password", self.authentication_service.get_session_stored()["user_password"])

                self.info_panel.log_text("Client: Username and password entered.")
                self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
                self.info_panel.log_text("Server: Registering username and Hashing password.")
                self.info_panel.log_text("Registeration successful.")

                self.message_service.send(self, "Registered", None)
            

class PasswordAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/authenticate_views/password_view.ui", self)

        self.info_panel.add_client_data("username", "null")
        self.info_panel.add_client_data("password", "null")
        
        self.info_panel.add_server_data("user_registered", self.authentication_service.get_session_stored()["user_registered"])
        self.info_panel.add_server_data("user_password", self.authentication_service.get_session_stored()["user_password"])

        self.info_panel.log_text("Waiting for username and password...")

        self.password_field.setEchoMode(QLineEdit.Password)
        self.submit_btn.clicked.connect(self.send)

    def send(self) -> None:
        if self.authentication_service.authenticate(self.username_field.text(), self.password_field.text()):
            self.info_panel.update_client_status("request", "authentication")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_authenticate"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user authenticated")

            self.info_panel.update_client_data("username", self.username_field.text())
            self.info_panel.update_client_data("password", self.password_field.text())

            self.info_panel.log_text("Client: Username and password entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Verifying username and password.")
            self.info_panel.log_text("Authentication successful.")

            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")
            self.password_field.clear()