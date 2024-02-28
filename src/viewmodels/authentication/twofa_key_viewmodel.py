from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QButtonGroup
from PyQt5.QtGui import QPixmap
from viewmodels.authentication.authentication_base import *
from configuration.app_configuration import Settings
from widgets.waiting_spinner import QtWaitingSpinner
import random
from models.utils import image_byte, byte_str, decode_key


# pyright: reportAttributeAccessIssue=false

class TwoFAKeyRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/twofa_key_view.ui", info_panel)

        self.key_on = False
        self.progress = 0
        self.prev_finger = "fp1"
        self.current_finger = ""
        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp1_btn)
        self.finger_group.addButton(self.fp4_btn)

        self.finger_group.buttonToggled.connect(self.on_finger_changed)
        self.fp1_btn.setChecked(True)

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
        self.warning_label.setVisible(False)

        self.w.start()

        self.connect_btn.clicked.connect(self.connect_device)
        self.next_btn.clicked.connect(self.prepare_fingerprint)
        self.security_key.clicked.connect(self.set_fingerprint)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), "expand")
        self.info_panel.add_client_data("Fingerprint Template", ("Fingerprint Template", "NULL"), "expand")
        self.info_panel.add_client_data("Private Key", ("Private Key", "NULL"), "expand")
        
        self.info_panel.add_server_data("User Key Name", "NULL")
        self.info_panel.add_server_data("User Key Handle", ("Key Handle", "NULL"), "expand")
        self.info_panel.add_server_data("User Public Key", ("User Public Key", "NULL"), "expand")

        self.info_panel.log_text("Waiting to activate two-FA key and scan fingerprint...")
        self.info_panel.set_measure_level(95)

    def connect_device(self) -> None:
        self.connect_btn.hide()
        self.key_on = True
        self.w.stop()
        self.waiting_label.hide()

        self.key_select_frame.show()
        self.guide_label.show()
        self.key_name_field.show()
        self.next_btn.show()

        self.security_key.setCursor(Qt.PointingHandCursor)

    def prepare_fingerprint(self) -> None:
        if len(self.key_name_field.text()) < 3:
            self.warning_label.setVisible(True)
        else:
            self.left_stacked.setCurrentIndex(self.left_stacked.currentIndex() + 1)

    def on_finger_changed(self, button, checked) -> None:
        if checked:
            match (button.objectName()):
                case "fp1_btn":
                    self.current_finger = "fp1"
                case "fp4_btn":
                    self.current_finger = "fp4"

    def set_fingerprint(self) -> None:
        if self.prev_finger != self.current_finger:
            self.progress = 0
            self.prev_finger = self.current_finger
        elif self.key_on and self.progress < 5:
            step = random.choice([1, 2])
            self.progress += step
            if self.progress >= 5:
                self.progress = 5
                self.instruction_label.setStyleSheet("color: #049c84")
                self.instruction_label.setText("Registration Completed")
                self.send()
        self.fingerprint.setPixmap(QPixmap(f"{Settings.IMAGE_FILE_PATH}fp_{self.progress}.png"))


    def send(self) -> None:
        key_name = self.key_name_field.text()
        
        fingerprint = image_byte("data/fingerprints/"+self.current_finger+".png")

        if self.authentication_service.register(fingerprint):
            self.info_panel.update_client_status("Registration", self.authentication_service.get_session_stored()["timestamp_register"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

            self.authentication_service.session_store({"key_name":key_name})
        
            self.info_panel.update_client_data("Fingerprint", ("Fingerprint in bytes", byte_str(fingerprint)), "expand")
            self.info_panel.update_client_data("Fingerprint Template", ("User Fingerprint Template",  byte_str(self.authentication_service.get_session_stored()["fingerprint_template"])),  "expand")
            self.info_panel.update_client_data("Private Key", ("Private Key", decode_key(self.authentication_service.get_session_stored()["private_key"])), "expand")

            self.info_panel.update_server_data("User Key Name", key_name)
            self.info_panel.update_server_data("User Key Handle", ("Key Handle", self.authentication_service.get_session_stored()["key_handle"]), "expand")
            self.info_panel.update_server_data("User Public Key", ("User Public Key", decode_key(self.authentication_service.get_session_stored()["public_key"])), "expand")

            self.info_panel.update_data_note(1)

            self.info_panel.log_text("Client: 2FA Key powered and activated.")
            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Converting fingerprint to fingerprint template and store inside 2FA key.")
            self.info_panel.log_text("Security key generating public-private key pair and a key handle that references the private key.")
            self.info_panel.log_text("Client: Sending public key, key handle and key name to the server through a secure communication channel.")
            self.info_panel.log_text("Server: Storing public key, key handle and key name that links to the user.")
            self.info_panel.log_text("Registration successful.")

            self.message_service.send(self, "Registered", None)
            

class TwoFAKeyAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/twofa_key_view.ui", info_panel)
        
        self.key_on = False
        self.progress = 0
        self.current_finger = ""
        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp1_btn)
        self.finger_group.addButton(self.fp4_btn)
        self.finger_group.buttonToggled.connect(self.on_finger_changed)
        self.fp1_btn.setChecked(True)

        self.w = QtWaitingSpinner(self.left_frame)
        self.waiting_label = QLabel("Waiting for security key connection...")

        self.left_frame.layout().addWidget(self.w)
        self.left_frame.layout().addWidget(self.waiting_label, alignment=Qt.AlignHCenter)

        self.key_select_frame.hide()
        self.fingerprint.hide()
        self.instruction_label.hide()

        self.w.start()

        self.connect_btn.clicked.connect(self.connect_device)
        self.security_key.clicked.connect(self.send)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), "expand")
        self.info_panel.add_client_data("Fingerprint Template", ("Fingerprint Template", byte_str(self.authentication_service.get_session_stored()["fingerprint_template"])), "expand")
        self.info_panel.add_client_data("Private Key", ("Private Key", decode_key(self.authentication_service.get_session_stored()["private_key"])), "expand")
        self.info_panel.add_client_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), "expand")
        self.info_panel.add_client_data("Signed Challenge", ("Signed Challenge", "NULL"), "expand")
        
        self.info_panel.add_server_data("User Key Name", self.authentication_service.get_session_stored()["key_name"])
        self.info_panel.add_server_data("User Key Handle", ("Key Handle", self.authentication_service.get_session_stored()["key_handle"]), "expand")
        self.info_panel.add_server_data("User Public Key", ("User Public Key", decode_key(self.authentication_service.get_session_stored()["public_key"])), "expand")
        self.info_panel.add_server_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), "expand")

        self.info_panel.log_text("Waiting to activate two-FA key and validate fingerprint...")

    def connect_device(self) -> None:
        self.connect_btn.hide()
        self.key_on = True
        self.w.stop()
        self.waiting_label.hide()

        self.key_select_frame.show()
        self.key_name.setText(self.authentication_service.get_session_stored()["key_name"])
        self.fingerprint.show()
        self.instruction_label.show()

        self.security_key.setCursor(Qt.PointingHandCursor)
        self.info_panel.log_text("Client: 2FA Key powered and activated.")

    def on_finger_changed(self, button, checked) -> None:
        if checked:
            match (button.objectName()):
                case "fp1_btn":
                    self.current_finger = "fp1"
                case "fp4_btn":
                    self.current_finger = "fp4"

    def authenticated(self, mode: int = 0) -> None:
        self.instruction_label.setStyleSheet("color: #049c84;")
        self.instruction_label.setText("The user has been authenticated.")

        self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode: # bypass mode
            self.info_panel.update_client_data("Fingerprint", ("Fingerprint", byte_str(self.authentication_service.get_session_stored()["fingerprint"])), "expand")

        self.info_panel.update_client_data("Nonce", ("Nonce for Challenge-Response Protocol", byte_str(self.authentication_service.get_session_stored()["nonce"])), "expand")
        self.info_panel.update_client_data("Signed Challenge", ("Signed Challenge", byte_str(self.authentication_service.get_session_stored()["signed_challenge"])), "expand")

        self.info_panel.update_server_data("Nonce", ("Nonce for Challenge-Response Protocol", byte_str(self.authentication_service.get_session_stored()["nonce"])), "expand")

        self.info_panel.log_text("Server: Generating challenge and sending challenge along with a key handle to client.")
        self.info_panel.log_text("Client: Scanning Fingerprint.")
        self.info_panel.log_text("Security key converting fingerprint to fingerprint template.")
        self.info_panel.log_text("Security key compares fingerprint template with stored features.")
        self.info_panel.log_text("Features matched.")
        self.info_panel.log_text("The security key retrieves the correct private key based on the key handle.")
        self.info_panel.log_text("Security key signs the challenge.")
        self.info_panel.log_text("Client: Sending the signed challenge to the server.")
        self.info_panel.log_text("Server: Verifing the signed challenge using the stored public key.")
        self.info_panel.log_text("Authentication successful.")

        self.message_service.send(self, "Authenticated", None)
        
    def send(self) -> None:
        if self.key_on:
            fingerprint = image_byte("data/fingerprints/"+self.current_finger+".png")

            if self.authentication_service.authenticate(fingerprint):
                self.authenticated()
            else:
                self.instruction_label.setStyleSheet("color: #d5786c;")
                self.instruction_label.setText("Your credentials do not match our record..")

                self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
                self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Server: Generating challenge and sent challenge along with key handle to client.")
                self.info_panel.log_text("Client: Scanning Fingerprint.")
                self.info_panel.log_text("Security key converting fingerprint to fingerprint template.")
                self.info_panel.log_text("Security key compares fingerprint template with stored features.")
                self.info_panel.log_text("Features unmatched.")
                self.info_panel.log_text("Authentication unsuccessful.")

            self.info_panel.update_client_data("Fingerprint", ("Fingerprint", byte_str(fingerprint)), "expand")