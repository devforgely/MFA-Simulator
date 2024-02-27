from PyQt5.QtWidgets import QButtonGroup
from PyQt5.QtGui import QPixmap, QIcon
from viewmodels.authentication.authentication_base import *
from configuration.app_configuration import Settings
import random
from models.utils import image_byte, byte_str

class FingerPrintRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/fingerprint_view.ui", info_panel)
        
        self.progress = 0
        self.prev_finger = "fp1"
        self.current_finger = ""

        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp1_btn)
        self.finger_group.addButton(self.fp2_btn)
        self.finger_group.addButton(self.fp3_btn)
        self.finger_group.addButton(self.fp4_btn)
        self.finger_group.addButton(self.fp5_btn)

        self.finger_group.buttonToggled.connect(self.on_finger_changed)
        self.fp1_btn.setChecked(True)

        self.fingerprint_btn.clicked.connect(self.set_fingerprint)
        self.initalise_infopanel()

        self.phone_frame.adjust_shadow(40, 60, 5, 5)

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), "expand")
        
        self.info_panel.add_server_data("User Fingerprint Template", ("User Fingerprint Template", "NULL"), "expand")

        self.info_panel.log_text("Waiting for fingerprint data...")
        self.info_panel.set_measure_level(75)

    def on_finger_changed(self, button, checked) -> None:
        if checked:
            match (button.objectName()):
                case "fp1_btn":
                    self.current_finger = "fp1"
                case "fp2_btn":
                    self.current_finger = "fp2"
                case "fp3_btn":
                    self.current_finger = "fp3"
                case "fp4_btn":
                    self.current_finger = "fp4"
                case "fp5_btn":
                    self.current_finger = "fp5"

    def set_fingerprint(self) -> None:
        if self.prev_finger != self.current_finger:
            self.progress = 0
            self.prev_finger = self.current_finger
        elif self.progress < 6:
            step = random.choice([1, 2])
            self.progress += step
            if self.progress >= 6:
                self.progress = 6

                self.fingerprint_btn.setEnabled(False)
                self.short_instruction.setText("Fingerprint added")
                self.long_instruction.setText("When you see the fingerprint icon, use your fingerprint to authenticate your identity.")
                self.instruction_label.setText("")
                self.instruction_label.setFixedSize(30, 30)
                self.instruction_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH+"tick-circle-green.svg"))
                self.send()
        self.fingerprint_btn.setIcon(QIcon(QPixmap(f"{Settings.IMAGE_FILE_PATH}fp{self.progress}.png")))

    def send(self) -> None:
        fingerprint = image_byte("data/fingerprints/"+self.current_finger+".png")

        if self.authentication_service.register(fingerprint):
            self.info_panel.update_client_status("Registration", self.authentication_service.get_session_stored()["timestamp_register"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

            self.info_panel.update_client_data("Fingerprint", ("Fingerprint in bytes", byte_str(fingerprint)), "expand")

            self.info_panel.update_server_data("User Fingerprint Template", ("User Fingerprint Template",  byte_str(self.authentication_service.get_session_stored()["fingerprint_template"])),  "expand")

            self.info_panel.update_data_note(1)

            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Converting fingerprint into fingerprint template.")
            self.info_panel.log_text("Server: Securely store the fingerprint template.")
            self.info_panel.log_text("Registration successful.")

            self.message_service.send(self, "Registered", None)
            

class FingerPrintAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/fingerprint_view.ui", info_panel)

        self.current_finger = ""

        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp1_btn)
        self.finger_group.addButton(self.fp2_btn)
        self.finger_group.addButton(self.fp3_btn)
        self.finger_group.addButton(self.fp4_btn)
        self.finger_group.addButton(self.fp5_btn)

        self.finger_group.buttonToggled.connect(self.on_finger_changed)
        self.fp1_btn.setChecked(True)

        self.warning_label.setVisible(False)

        self.fingerprint_btn.clicked.connect(self.send)
        self.initalise_infopanel()

        self.phone_frame.adjust_shadow(40, 60, 5, 5)

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), "expand")
        
        self.info_panel.add_server_data("User Fingerprint Template", ("User Fingerprint Template", byte_str(self.authentication_service.get_session_stored()["fingerprint_template"])), "expand")

        self.info_panel.log_text("Waiting for fingerprint data...")

    def on_finger_changed(self, button, checked) -> None:
        if checked:
            match (button.objectName()):
                case "fp1_btn":
                    self.current_finger = "fp1"
                case "fp2_btn":
                    self.current_finger = "fp2"
                case "fp3_btn":
                    self.current_finger = "fp3"
                case "fp4_btn":
                    self.current_finger = "fp4"
                case "fp5_btn":
                    self.current_finger = "fp5"

    def authenticated(self, mode: int = 0) -> None:
        self.warning_label.setStyleSheet("color: #049c84")
        self.warning_label.setText("The user has been authenticated.")
        self.warning_label.setVisible(True)
        self.fingerprint_btn.setEnabled(False)

        self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode: # bypass mode
            self.info_panel.update_client_data("Fingerprint", ("Fingerprint", byte_str(self.authentication_service.get_session_stored()["fingerprint"])), "expand")

        self.info_panel.log_text("Client: Fingerprint scanned.")
        self.info_panel.log_text("Client: Sending data through a secure communication channel.")
        self.info_panel.log_text("Server: Converting data to fingerprint template.")
        self.info_panel.log_text("Server: Comparing fingerprint features.")
        self.info_panel.log_text("Authentication successful.")

        self.message_service.send(self, "Authenticated", None)
    

    def send(self) -> None:
        fingerprint = image_byte("data/fingerprints/"+self.current_finger+".png")

        if self.authentication_service.authenticate(fingerprint):
            self.authenticated()
        else:  
            self.warning_label.setVisible(True)

            self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
            self.info_panel.update_data_note(1)

            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Converting data to fingerprint template.")
            self.info_panel.log_text("Server: Comparing fingerprint features.")
            self.info_panel.log_text("Authentication unsuccessful.")
        
        self.info_panel.update_client_data("Fingerprint", ("Fingerprint", byte_str(fingerprint)), "expand")