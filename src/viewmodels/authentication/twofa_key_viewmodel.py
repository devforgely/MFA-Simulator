from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from viewmodels.authentication.authentication_base import *
from configuration.app_configuration import Settings
from widgets.waiting_spinner import QtWaitingSpinner
import uuid
import random
import string


# pyright: reportAttributeAccessIssue=false

class TwoFAKeyRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/twofa_key_view.ui", info_panel)
        
        self.key_on = False
        self.progress = 0
        self.w = QtWaitingSpinner(self.page1)

        self.waiting_label = QLabel("Waiting for security key connection...")

        self.next_btn = QPushButton('Next')
        self.next_btn.setMinimumWidth(100)
        self.next_btn.setMinimumHeight(35)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        
        self.page1.layout().addWidget(self.w)
        self.page1.layout().addWidget(self.waiting_label, alignment=Qt.AlignHCenter)
        self.page1.layout().addWidget(self.next_btn, alignment=Qt.AlignRight)

        self.key_select_frame.hide()
        self.guide_label.hide()
        self.key_name_field.hide()
        self.next_btn.hide()

        self.w.start()

        self.connect_btn.clicked.connect(self.connect_device)
        self.on_btn.clicked.connect(self.activiate_device)
        self.next_btn.clicked.connect(lambda: self.left_stacked.setCurrentIndex(self.left_stacked.currentIndex() + 1))
        self.security_key.clicked.connect(self.set_fingerprint)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("key_id", "null")
        self.info_panel.add_client_data("key_name", "null")
        self.info_panel.add_client_data("fingerprint", "null")
        self.info_panel.add_client_data("fingerprint_template", "null")
        self.info_panel.add_client_data("shared_key", "null")
        
        self.info_panel.add_server_data("user_key_id", "null")
        self.info_panel.add_server_data("user_key_name", "null")
        self.info_panel.add_server_data("shared_key", "null")

        self.info_panel.log_text("Waiting for two-FA key...")

    def connect_device(self) -> None:
        self.on_btn.setEnabled(True)
        self.connect_btn.hide()

    def activiate_device(self) -> None:
        self.key_on = True
        self.on_btn.setEnabled(False)
        self.w.stop()
        self.waiting_label.hide()

        self.key_select_frame.show()
        self.guide_label.show()
        self.key_name_field.show()
        self.next_btn.show()

        self.security_key.setCursor(Qt.PointingHandCursor)

    def set_fingerprint(self) -> None:
        if self.key_on and self.progress < 5:
            step = random.choice([1, 2])
            self.progress += step
            if self.progress >= 5:
                self.progress = 5
                self.instruction_label.setText("Registration Completed")
                self.send()
            self.fingerprint.setPixmap(QPixmap(f"{Settings.IMAGE_FILE_PATH}fp_{self.progress}.png"))
                
    def send(self) -> None:
        key_id = str(uuid.uuid4())
        key_name = self.key_name_field.text()
        characters = string.ascii_letters + string.digits
        simulated_fingerprint_data = ''.join(random.choice(characters) for _ in range(300))
        simulated_fingerprint_template = ''.join(random.choice(characters) for _ in range(100))
        
        if self.authentication_service.register():
            self.authentication_service.session_store({"user_key_id":key_id, "user_key_name":key_name, 
                                                       "fingerprint_template": simulated_fingerprint_template})
            
            self.info_panel.update_client_status("request", "registration")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user registered")
            
            self.info_panel.update_client_data("key_id", key_id)
            self.info_panel.update_client_data("key_name", key_name)
            self.info_panel.update_client_data("fingerprint", simulated_fingerprint_data)
            self.info_panel.update_client_data("fingerprint_template", simulated_fingerprint_template)
            self.info_panel.update_client_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])

            self.info_panel.update_client_data("user_key_id", key_id)
            self.info_panel.update_client_data("user_key_name", key_name)
            self.info_panel.update_server_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])

            self.info_panel.log_text("Client: 2FA Key powered and activated.")
            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Converting fingerprint to fingerprint template and store inside 2FA key.")
            self.info_panel.log_text("Client: Generate and send shared_key through HTTPS protocol.")
            self.info_panel.log_text("Server: Storing shared key and user identification.")
            self.info_panel.log_text("Registration successful.")

            self.message_service.send(self, "Registered", None)
            

class TwoFAKeyAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/twofa_key_view.ui", info_panel)
        
        self.key_on = False
        self.progress = 0
        self.w = QtWaitingSpinner(self.left_frame)
        self.waiting_label = QLabel("Waiting for security key connection...")

        self.left_frame.layout().addWidget(self.w)
        self.left_frame.layout().addWidget(self.waiting_label, alignment=Qt.AlignHCenter)

        self.key_select_frame.hide()
        self.fingerprint.hide()
        self.instruction_label.hide()

        self.w.start()

        self.connect_btn.clicked.connect(self.connect_device)
        self.on_btn.clicked.connect(self.activiate_device)
        self.security_key.clicked.connect(self.send)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("key_id", self.authentication_service.get_session_stored()["user_key_id"])
        self.info_panel.add_client_data("key_name", self.authentication_service.get_session_stored()["user_key_name"])
        self.info_panel.add_client_data("fingerprint", "null")
        self.info_panel.add_client_data("fingerprint_template", self.authentication_service.get_session_stored()["fingerprint_template"])
        self.info_panel.add_client_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])
        
        self.info_panel.add_server_data("user_key_id", self.authentication_service.get_session_stored()["user_key_id"])
        self.info_panel.add_server_data("user_key_name", self.authentication_service.get_session_stored()["user_key_name"])
        self.info_panel.add_server_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])

        self.info_panel.log_text("Waiting for two-FA key...")

    def connect_device(self) -> None:
        self.on_btn.setEnabled(True)
        self.connect_btn.hide()

    def activiate_device(self) -> None:
        self.key_on = True
        self.on_btn.setEnabled(False)
        self.w.stop()
        self.waiting_label.hide()

        self.key_select_frame.show()
        self.key_name.setText(self.authentication_service.get_session_stored()["user_key_name"])
        self.fingerprint.show()
        self.instruction_label.show()

        self.security_key.setCursor(Qt.PointingHandCursor)

    def send(self) -> None:
        self.authentication_service.authenticate("") # empty string generates time based code
        characters = string.ascii_letters + string.digits
        simulated_fingerprint_data = ''.join(random.choice(characters) for _ in range(300))
        self.info_panel.update_client_data("fingerprint", simulated_fingerprint_data)

        if self.authentication_service.authenticate(self.authentication_service.get_session_stored()["totp"]):
            self.instruction_label.setText("Identity Verified")

            self.info_panel.update_client_status("request", "authentication")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_authenticate"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user authenticated")

            self.info_panel.log_text("Client: 2FA Key powered and activated.")
            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Converting fingerprint to fingerprint template")
            self.info_panel.log_text("Client: Comparing fingerprint template with stored features.")
            self.info_panel.log_text("Client: Features matched.")
            self.info_panel.log_text("Client: Approve 2FA Key to generate code and send through HTTPS protocol.")
            self.info_panel.log_text("Server: Calculating code based on time and shared_key.")
            self.info_panel.log_text("Server: Comparing code.")
            self.info_panel.log_text("Authentication successful.")

            self.message_service.send(self, "Authenticated", None)
        else:
            QMessageBox.warning(self, "Error", "Authentication failed. Try again.")