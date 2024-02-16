from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from viewmodels.authentication.authentication_base import *
from configuration.app_settings import Settings
import random

class FingerPrintRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/fingerprint_view.ui", info_panel)
        
        self.progress = 0

        self.fingerprint_btn.clicked.connect(self.set_fingerprint)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("fingerprint", "null")
        
        self.info_panel.add_server_data("user_fingerprint", "null")

        self.info_panel.log_text("Waiting for fingerprint...")

    def set_fingerprint(self) -> None:
        if self.progress < 6:
            step = random.choice([1, 2])
            self.progress += step
            if self.progress >= 6:
                self.progress = 6
                self.instruction_label.setText("Registeration Completed")
                self.send()
            self.fingerprint_btn.setIcon(QIcon(QPixmap(f"{Settings.IMAGE_FILE_PATH}fp{self.progress}.png")))

    def send(self) -> None:
        if self.authentication_service.register('data/fingerprints/fp1.png'):
            self.info_panel.update_client_status("request", "registration")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user registered")

            self.info_panel.update_client_data("fingerprint", "data/fingerprints/fp1.png")

            self.info_panel.update_server_data("user_fingerprint", self.authentication_service.get_session_stored()["key"])

            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Converting fingerprint into fingerprint template.")
            self.info_panel.log_text("Server: Hashing fingerprint template")
            self.info_panel.log_text("Registeration successful.")

            self.message_service.send(self, "Registered", None)
            

class FingerPrintAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/fingerprint_view.ui", info_panel)

        self.fingerprint_btn.clicked.connect(self.send)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("fingerprint", "null")
        
        self.info_panel.add_server_data("user_fingerprint", self.authentication_service.get_session_stored()["key"])

        self.info_panel.log_text("Waiting for fingerprint...")

    def send(self) -> None:
        if random.random() < 0.4:
            self.info_panel.update_client_data("fingerprint", "data/fingerprints/fp3.png")
            QMessageBox.warning(self, "Error", "Authenticate fingerprint failed. Try again.")
        else:
            if self.authentication_service.authenticate('data/fingerprints/fp1.png'):
                self.info_panel.update_client_status("request", "authentication")
                self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_authenticate"])

                self.info_panel.update_server_status("status", "200")
                self.info_panel.update_server_status("message", "user authenticated")

                self.info_panel.update_client_data("fingerprint", "data/fingerprints/fp1.png")

                self.info_panel.log_text("Client: Fingerprint scanned.")
                self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
                self.info_panel.log_text("Server: Converting data to fingerprint template.")
                self.info_panel.log_text("Server: Comparing fingerprint features.")
                self.info_panel.log_text("Authentication successful.")

                self.message_service.send(self, "Authenticated", None)
            else:
                self.info_panel.update_client_data("fingerprint", "data/fingerprints/fp2.png")
                print("wrong key")