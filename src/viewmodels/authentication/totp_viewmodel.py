from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QColor
from PyQt5.QtWidgets import QMessageBox, QGraphicsDropShadowEffect
from viewmodels.authentication.authentication_base import *
from widgets.timer import TimeThread
import uuid
from datetime import datetime, timezone
import re

# pyright: reportAttributeAccessIssue=false

class TOTPRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/totp_view.ui", info_panel)

        self.country_dialing_codes = {
            "United Kingdom": "+44",
            "United States": "+1",
            "France": "+33",
            "Germany": "+49",
            "Australia": "+61",
            "Italy": "+39",
            "Spain": "+34",
            "China": "+86"
        }
        self.device_id = str(uuid.uuid4())

        self.number_layout.setAlignment(Qt.AlignLeft)

        self.country_box.currentIndexChanged.connect(lambda: 
            self.dialing_code.setText(self.country_dialing_codes[self.country_box.currentText()]))
        
        self.number_field.setValidator(QIntValidator())

        self.setup_btn.clicked.connect(self.next_instruction)
        self.continue_btn.clicked.connect(self.continue_after_number)
        self.scan_btn.clicked.connect(self.next_phone_screen)
        self.link_btn.clicked.connect(self.send)
        self.cancel_btn.clicked.connect(self.cancel)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("device_id", self.device_id)
        self.info_panel.add_client_data("phone_number", "null")
        self.info_panel.add_client_data("shared_key", "null")
        
        self.info_panel.add_server_data("user_device_id", "null")
        self.info_panel.add_server_data("user_phone_number", "null")
        self.info_panel.add_server_data("shared_key", "null")

        self.info_panel.log_text("Waiting for phone number...")

    def validate_number(self) -> bool:
        dialing_code = self.dialing_code.text()

        # Create a regex pattern for the phone number
        pattern = re.compile(r"^" + re.escape(dialing_code) + r"\d{8,15}$")

        # Check if the number matches the pattern
        return bool(pattern.match(dialing_code+self.number_field.text()))

    def next_instruction(self) -> None:
        self.left_stacked.setCurrentIndex(self.left_stacked.currentIndex() + 1)
    
    def next_phone_screen(self) -> None:
        self.phone_container.setCurrentIndex(self.phone_container.currentIndex() + 1)
        if self.phone_container.currentIndex() == 2:
            self.location_label.setText("Manchester, ENG, GB")
            self.time_label.setText(datetime.now(timezone.utc).strftime("%H:%M %Z"))
            self.device_label.setText("79.195.101.141")
            self.user_label.setText("m91341fa")

    def continue_after_number(self) -> None:
        if self.number_field.text() != "" and self.validate_number():
            self.next_instruction()
            self.next_phone_screen()
    
    def cancel(self) -> None:
        self.left_stacked.setCurrentIndex(0)
        self.phone_container.setCurrentIndex(0)
        self.number_field.setText("")

    def send(self) -> None:
        if self.authentication_service.register():
            self.link_btn.setEnabled(False)
            self.cancel_btn.hide()
            self.authentication_service.session_store({"user_device_id":self.device_id, 
                                                       "user_phone_number": self.dialing_code.text()+self.number_field.text()})
            
            self.info_panel.update_client_status("request", "registration")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user registered")

            self.info_panel.update_client_data("device_id", self.device_id)
            self.info_panel.update_client_data("phone_number", self.dialing_code.text()+self.number_field.text())
            self.info_panel.update_client_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])

            self.info_panel.update_server_data("user_device_id", self.authentication_service.get_session_stored()["user_device_id"])
            self.info_panel.update_server_data("user_phone_number", self.authentication_service.get_session_stored()["user_phone_number"])
            self.info_panel.update_server_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])

            self.info_panel.log_text("Client: phone number entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Sending QR code for shared key")
            self.info_panel.log_text("Client: Storing shared key")
            self.info_panel.log_text("Registeration successful.")

            self.message_service.send(self, "Registered", None)

class TOTPAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/totp_view.ui", info_panel)

        # thread for timer
        self.max_time = 30
        self.threading = TimeThread(self.max_time)
        self.threading._signal.connect(self.signal_update)
        self.time_bar.setMaximum(self.threading.MaxValue())

        number = self.authentication_service.get_session_stored()["user_phone_number"]
        self.hidden_number = number[:3] + (len(number)-6)*"x"+number[-3:]

        self.left_frame.layout().setAlignment(Qt.AlignTop)
        self.instruction_layout.setAlignment(Qt.AlignHCenter)
        self.bottom_layout.setAlignment(Qt.AlignHCenter)
        self.button_group_layout.setAlignment(Qt.AlignHCenter)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        shadow_effect.setBlurRadius(40)
        shadow_effect.setXOffset(2)
        self.left_frame.setGraphicsEffect(shadow_effect)

        self.time_bar.setVisible(False)

        self.code_field.setValidator(QIntValidator())
        
        self.code_btn.clicked.connect(self.get_code)
        self.verify_btn.clicked.connect(self.send)
        self.not_login_btn.clicked.connect(self.cancel)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("device_id", self.authentication_service.get_session_stored()["user_device_id"])
        self.info_panel.add_client_data("phone_number", self.authentication_service.get_session_stored()["user_phone_number"])
        self.info_panel.add_client_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])
        self.info_panel.add_client_data("totp", "null")
        
        self.info_panel.add_server_data("user_device_id", self.authentication_service.get_session_stored()["user_device_id"])
        self.info_panel.add_server_data("user_phone_number", self.authentication_service.get_session_stored()["user_phone_number"])
        self.info_panel.add_server_data("shared_key", self.authentication_service.get_session_stored()["shared_key"])
        self.info_panel.add_server_data("sha1_hash", "null")
        self.info_panel.add_server_data("totp", "null")

        self.info_panel.log_text("Waiting for TOTP...")
    
    def cancel(self) -> None:
        self.code_label.setText("000000")
        self.code_field.setText("")
        self.phone_container.setCurrentIndex(0)

    def get_code(self) -> None:
        # generate totp if empty string
        self.authentication_service.authenticate("")
        self.time_bar.setVisible(True)
        self.sent_label.setText(f"Sent to mobile ({self.hidden_number})")
        totp = self.authentication_service.get_session_stored()["totp"]
        self.code_label.setText(totp)
        self.phone_container.setCurrentIndex(self.phone_container.currentIndex() + 1)
        self.location_label.setText("Manchester, ENG, GB")
        self.time_label.setText(datetime.now(timezone.utc).strftime("%H:%M %Z"))
        self.code_btn.setVisible(False)

        self.threading.start()

    def signal_update(self, val: int):
        self.time_bar.setValue(val)
        self.time_bar.update()
        
        if val == 0:
            self.time_bar.setVisible(False)
            self.sent_label.setText(f"Code expired, please try again.")
            self.code_btn.setVisible(True)

    def send(self) -> None:
        self.info_panel.update_client_data("totp", self.code_field.text())

        if self.authentication_service.authenticate(self.code_field.text()):
            self.threading.stop()
            self.code_field.setEnabled(False)
            self.verify_btn.setEnabled(False)
            self.time_bar.setVisible(False)
            self.not_login_btn.hide()

            self.info_panel.update_client_status("request", "authentication")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_authenticate"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user authenticated")

            self.info_panel.log_text("Client: TOTP entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Verifying TOTP.")
            self.info_panel.log_text("Authentication successful.")

            self.message_service.send(self, "Authenticated", None)
        else:
            QMessageBox.warning(self, "Error", "Authentication failed. Try again.")
        
        self.info_panel.update_server_data("sha1_hash", self.authentication_service.get_session_stored()["sha1_hash"])
        self.info_panel.update_server_data("totp", self.authentication_service.get_session_stored()["totp"])