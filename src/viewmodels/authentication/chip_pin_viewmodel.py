from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QIcon, QPixmap
from viewmodels.authentication.authentication_base import *
from configuration.app_configuration import Settings
import random
from models.utils import byte_str

# pyright: reportAttributeAccessIssue=false

class ButtonHoverWatcher(QObject):
    def __init__(self, button, default_image: str, hover_image: str)-> None:
        super().__init__(button)
        self.button = button
        self.default_icon = default_image
        self.hover_icon = hover_image

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Enter:
            # The push button is hovered by mouse
            self.button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}{self.hover_icon}.svg"))
        elif event.type() == QEvent.Leave:
            # The push button is not hovered by mouse
            self.button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}{self.default_icon}.svg"))
        return super().eventFilter(watched, event)

class ChipPinRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/chip_pin_view.ui", info_panel)

        self.pin_entered = ""
        self.allow_pin = True

        self.generate_pin_btn.clicked.connect(self.generate_pin)

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

        self.clear_btn.installEventFilter(ButtonHoverWatcher(self.clear_btn, "delete", "delete-red"))
        self.submit_btn.installEventFilter(ButtonHoverWatcher(self.submit_btn, "tick-circle", "tick-circle-green"))

        self.warning_label.setVisible(False)
        self.frame.adjust_shadow(30, 50, 2, 2)
    
        self.initalise_infopanel()
    
    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Pin", "NULL")
        self.info_panel.add_client_data("Chip Store of Hashed Pin", ("Chip Store of Hashed Pin", "NULL"), "expand")
        self.info_panel.add_client_data("Chip Details", ("Chip Details in Bytes", "NULL"), "expand")
        self.info_panel.add_client_data("Chip Digital Signature", ("Chip Digital Signature", "NULL"), "expand")

        self.info_panel.add_server_data("User Chip Details", ("User Chip Details in Bytes", "NULL"), "expand")
        self.info_panel.add_server_data("User Chip Digital Signature", ("User Chip Digital Signature", "NULL"), "expand")
        
        self.info_panel.log_text("Waiting to create a new chip card and assign a pin...")
        self.info_panel.set_measure_level(90)

    def generate_pin(self) -> None:
        # Generate a random 6-digit PIN, use more secure pseudo random number generator in real world
        self.pin_field.setText(str(random.randint(100000, 999999)))

    def update_field(self, char: str) -> None:
        if self.allow_pin:
            if char == "$":
                self.pin_field.setText("")
            else:
                self.pin_field.setText(self.pin_field.text()+char)

    def send(self) -> None:
        plain_pin = self.pin_field.text()
        if not self.pin_entered and len(plain_pin) < 4:
            self.warning_label.setText("PIN must be atleast 4 digits long.")
            self.warning_label.setVisible(True)
        elif not self.pin_entered:
            self.pin_entered = plain_pin
            self.pin_field.setText("")
            self.pin_field.setPlaceholderText("Re-Enter PIN")
            self.pin_field.setEchoMode(QLineEdit.Password)
            self.generate_pin_btn.setEnabled(False)    
        elif plain_pin != self.pin_entered: # restart the whole process
            self.pin_entered = ""
            self.pin_field.setText("")
            self.pin_field.setPlaceholderText("Choose PIN")
            self.pin_field.setEchoMode(QLineEdit.Normal)
            self.generate_pin_btn.setEnabled(True)  

            self.warning_label.setText("PIN did not match.")
            self.warning_label.setVisible(True)
        else:
            if self.authentication_service.register(self.pin_entered):
                self.chip_card.setPixmap(QPixmap(Settings.IMAGE_FILE_PATH+"chip_card.png"))
                self.warning_label.setStyleSheet("color: #049c84")
                self.warning_label.setText("Account registered and card received.")
                self.warning_label.setVisible(True)
                self.submit_btn.setEnabled(False)
                self.clear_btn.setEnabled(False)
                self.allow_pin = False

                self.info_panel.update_client_status("Registration", self.authentication_service.get_session_stored()["timestamp_register"])
                self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

                self.info_panel.update_client_data("Pin", self.pin_entered)
                self.info_panel.update_client_data("Chip Store of Hashed Pin", ("Chip Store of Hashed Pin", byte_str(self.authentication_service.get_session_stored()["hashed_pin"])), "expand")
                self.info_panel.update_client_data("Chip Details", ("Chip Details in Bytes", str(self.authentication_service.get_session_stored()["chip_details"])), "expand")
                self.info_panel.update_client_data("Chip Digital Signature", ("Chip Digital Signature", byte_str(self.authentication_service.get_session_stored()["chip_digital_signature"])), "expand")

                self.info_panel.update_server_data("User Chip Details", ("User Chip Details in Bytes", str(self.authentication_service.get_session_stored()["chip_details"])), "expand")
                self.info_panel.update_server_data("User Chip Digital Signature", ("User Chip Digital Signature", byte_str(self.authentication_service.get_session_stored()["chip_digital_signature"])), "expand")

                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Client: Pin entered.")
                self.info_panel.log_text("Programming hashed pin into the chip, adding chip details and digital signature.")
                self.info_panel.log_text("Server: Storing chip details and digital signature.")
                self.info_panel.log_text("Sending chip to the client.")
                self.info_panel.log_text("Registration successful.")

                self.message_service.send(self, "Registered", None)


class ChipPinAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/chip_pin_view.ui", info_panel)

        self.chip_card.set_collision(self.terminal)
        self.chip_card.set_collision_call(self.insert_card)
        self.allow_pin = False

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

        self.clear_btn.installEventFilter(ButtonHoverWatcher(self.clear_btn, "delete", "delete-red"))
        self.submit_btn.installEventFilter(ButtonHoverWatcher(self.submit_btn, "tick-circle", "tick-circle-green"))
        self.warning_label.setVisible(False)
        self.frame.adjust_shadow(30, 50, 2, 2)

        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Pin", "NULL")
        self.info_panel.add_client_data("Chip Store of Hashed Pin", ("Chip Store of Hashed Pin", byte_str(self.authentication_service.get_session_stored()["hashed_pin"])), "expand")
        self.info_panel.add_client_data("Chip Details", ("Chip Details in Bytes", str(self.authentication_service.get_session_stored()["chip_details"])), "expand")
        self.info_panel.add_client_data("Chip Digital Signature", ("Chip Digital Signature", byte_str(self.authentication_service.get_session_stored()["chip_digital_signature"])), "expand")
        self.info_panel.add_client_data("ARQC", ("Authorization Request Cryptogram", "NULL"), "expand")

        self.info_panel.add_server_data("User Chip Details", ("User Chip Details in Bytes", str(self.authentication_service.get_session_stored()["chip_details"])), "expand")
        self.info_panel.add_server_data("User Chip Digital Signature", ("User Chip Digital Signature", byte_str(self.authentication_service.get_session_stored()["chip_digital_signature"])), "expand")
        self.info_panel.add_server_data("ARPC", ("Authorization Response Cryptogram", "NULL"), "expand")

        self.info_panel.log_text("Waiting to insert card then validate pin...")

    def insert_card(self) -> None:
        self.terminal.setPixmap(QPixmap(Settings.IMAGE_FILE_PATH+"card_inside.png"))
        self.pin_field.setPlaceholderText("Enter PIN")
        self.allow_pin = True

    def update_field(self, char: str) -> None:
        if self.allow_pin:
            if char == "$":
                self.pin_field.setText("")
            else:
                self.pin_field.setText(self.pin_field.text()+char)

    def authenticated(self, mode: int = 0) -> None:
        self.warning_label.setStyleSheet("color: #049c84")
        self.warning_label.setText("The user has been authenticated.")
        self.warning_label.setVisible(True)
        self.submit_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.allow_pin = False

        self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode: # bypass mode
            self.info_panel.update_client_data("Pin", self.authentication_service.get_session_stored()["pin"])

        self.info_panel.update_client_data("ARQC", ("Authorization Request Cryptogram", byte_str(self.authentication_service.get_session_stored()["arqc"])), "expand")
        self.info_panel.update_server_data("ARPC", ("Authorization Response Cryptogram", byte_str(self.authentication_service.get_session_stored()["arpc"])), "expand")

        self.info_panel.log_text("Client: Pin entered.")
        self.info_panel.log_text("Card: Hashing pin and validate against hashed pin stored in the chip.")
        self.info_panel.log_text("Card: Generate ARQC with request detail and digital signature.")
        self.info_panel.log_text("Card: Sending ARQC to the terminal.")
        self.info_panel.log_text("Server: Received ARQC from terminal, verifying ARQC then sending back ARPC.")
        self.info_panel.log_text("Authentication successful.")

        self.message_service.send(self, "Authenticated", None)

    def send(self) -> None:
        if self.allow_pin:
            plain_pin = self.pin_field.text()

            if self.authentication_service.authenticate(plain_pin):
                self.authenticated()     
            else:
                self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
                self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Client: Pin entered.")
                self.info_panel.log_text("Card: Hashing pin and validate against hashed pin stored in the chip.")
                self.info_panel.log_text("Card: The PIN entered does not match in the memory.")
                self.info_panel.log_text("Authentication unsuccessful.")

                self.pin_field.clear()
                self.warning_label.setVisible(True)

            self.info_panel.update_client_data("Pin", plain_pin)
