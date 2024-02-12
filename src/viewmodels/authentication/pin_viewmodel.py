from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QIcon
from viewmodels.authentication.authentication_base import *
import uuid
import rsa
import hashlib
import base64

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
            self.button.setIcon(QIcon(f"resources/icons/{self.hover_icon}.svg"))
        elif event.type() == QEvent.Leave:
            # The push button is not hovered by mouse
            self.button.setIcon(QIcon(f"resources/icons/{self.default_icon}.svg"))
        return super().eventFilter(watched, event)

class PinRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/pin_view.ui", info_panel)

        self.device_id = str(uuid.uuid4())

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
        self.clear_btn.setStyleSheet("""
            QPushButton:hover {
                background-color: none;
            }
        """)

        self.submit_btn.installEventFilter(ButtonHoverWatcher(self.submit_btn, "tick-circle", "tick-circle-green"))
        self.submit_btn.setStyleSheet("""
            QPushButton:hover {             
                background-color: none;
            }
        """)
        self.initalise_infopanel()
    
    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("device_id", self.device_id)
        self.info_panel.add_client_data("pin", "null")
        self.info_panel.add_client_data("hashed_pin", "null")
        self.info_panel.add_client_data("user_private_key", "null")

        self.info_panel.add_server_data("user_public_key", "null")

        self.info_panel.log_text("Waiting for pin...")

    def update_field(self, char: str) -> None:
        if char == "$":
            self.pin_field.setText("")
        else:
            self.pin_field.setText(self.pin_field.text()+char)

    def send(self) -> None:
        plain_pin = self.pin_field.text()

        if len(plain_pin) < 3: return

        public_key, private_key = rsa.newkeys(512)

        if self.authentication_service.register(public_key.save_pkcs1()):
            secret = hashlib.sha256(plain_pin.encode()).hexdigest()
            self.authentication_service.session_store({
                "secret": secret, "device_id": self.device_id, "private_key": private_key.save_pkcs1()})

            self.info_panel.update_client_status("request", "registration")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user registered")

            self.info_panel.update_client_data("user_private_key", private_key.save_pkcs1().decode())
            self.info_panel.update_client_data("pin", plain_pin)
            self.info_panel.update_client_data("hashed_pin", secret)

            self.info_panel.update_server_data("user_public_key", public_key.save_pkcs1().decode())

            self.info_panel.log_text("Client: Pin created locally.")
            self.info_panel.log_text("Client: Generating asymmetric key-pair.")
            self.info_panel.log_text("Server: Registering user public key in identity provider.")
            self.info_panel.log_text("Registeration successful.")

            self.message_service.send(self, "Registered", None)


class PinAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/pin_view.ui", info_panel)

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
        self.clear_btn.setStyleSheet("""
            QPushButton:hover {
                background-color: none;
            }
        """)

        self.submit_btn.installEventFilter(ButtonHoverWatcher(self.submit_btn, "tick-circle", "tick-circle-green"))
        self.submit_btn.setStyleSheet("""
            QPushButton:hover {             
                background-color: none;
            }
        """)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.stored = self.authentication_service.get_session_stored()
        self.info_panel.add_client_data("device_id", self.stored["device_id"])
        self.info_panel.add_client_data("pin", "null")
        self.info_panel.add_client_data("hashed_pin", self.stored["secret"])
        self.info_panel.add_client_data("server_challenge", "null")
        self.info_panel.add_client_data("user_private_key", self.stored["private_key"].decode())

        self.info_panel.add_server_data("user_public_key", self.stored["public_key"].decode())

        self.info_panel.log_text("Waiting for pin...")

    def update_field(self, char: str) -> None:
        if char == "$":
            self.pin_field.setText("")
        else:
            self.pin_field.setText(self.pin_field.text()+char)

    def send(self) -> None:
        plain_pin = self.pin_field.text()

        if hashlib.sha256(plain_pin.encode()).hexdigest() == self.stored["secret"] \
            and self.authentication_service.authenticate(
                rsa.sign(self.stored["server_challenge"], rsa.PrivateKey.load_pkcs1(self.stored["private_key"]), 'SHA-256')):

            self.info_panel.update_client_status("request", "authentication")
            self.info_panel.update_client_status("timestamp", self.stored["timestamp_authenticate"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user authenticated")

            self.info_panel.update_client_data("pin", plain_pin)
            self.info_panel.update_client_data("server_challenge", str(base64.b64encode(self.stored["server_challenge"])))

            self.info_panel.log_text("Client: Pin entered locally.")
            self.info_panel.log_text("Server: Sending challenge to client.")
            self.info_panel.log_text("Client: Verifing pin and Local System unlocks private key.")
            self.info_panel.log_text("Client: Signing challenge with private key.")
            self.info_panel.log_text("Server: Verifing signed challenge.")
            self.info_panel.log_text("Authentication successful.")

            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")
            self.pin_field.clear()
