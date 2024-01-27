from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QColor
from PyQt5.QtWidgets import QMessageBox, QGraphicsDropShadowEffect
from viewmodels.authentication.authentication_base import *
import uuid
import random
from datetime import datetime, timezone
import re

# pyright: reportGeneralTypeIssues=false

class PushNotificationRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/push_notification_view.ui", info_panel)

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

        self.number_layout.setAlignment(Qt.AlignLeft)

        self.country_box.currentIndexChanged.connect(lambda: 
            self.dialing_code.setText(self.country_dialing_codes[self.country_box.currentText()]))
        
        self.number_field.setValidator(QIntValidator())

        self.setup_btn.clicked.connect(self.next_instruction)
        self.continue_btn.clicked.connect(self.continue_after_number)
        self.scan_btn.clicked.connect(self.next_phone_screen)
        self.link_btn.clicked.connect(self.send)
        self.cancel_btn.clicked.connect(self.cancel)

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
        device_id = str(uuid.uuid4())
        if self.authentication_service.register(device_id+";"+self.dialing_code.text()+self.number_field.text()):
            self.link_btn.setEnabled(False)
            self.cancel_btn.hide()
            self.authentication_service.session_store({"user_device_id":device_id, 
                                                       "user_phone_number": self.dialing_code.text()+self.number_field.text()})
            self.message_service.send(self, "Registered", None)
            

class PushNotificationAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/push_notification_view.ui", info_panel)
        
        self.stored = self.authentication_service.get_session_stored()
        number = self.stored["user_phone_number"]
        hidden_number = number[:3] + (len(number)-6)*"x"+number[-3:]

        self.left_frame.layout().setAlignment(Qt.AlignTop)
        self.instruction_layout.setAlignment(Qt.AlignHCenter)
        self.bottom_layout.setAlignment(Qt.AlignHCenter)
        self.button_group_layout.setAlignment(Qt.AlignHCenter)

        self.sent_label.setText(f"Sent to mobile ({hidden_number})")

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        shadow_effect.setBlurRadius(40)
        shadow_effect.setXOffset(2)
        self.left_frame.setGraphicsEffect(shadow_effect)
        
        self.code_btn.clicked.connect(self.send_code)
        self.verify_btn.clicked.connect(self.send)
        self.not_login_btn.clicked.connect(self.cancel)
    
    def cancel(self) -> None:
        self.code_label.setText("000000")
        self.code_field.setText("")
        self.phone_container.setCurrentIndex(0)

    def send_code(self) -> None:
        otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
        self.code_label.setText(otp)
        self.phone_container.setCurrentIndex(self.phone_container.currentIndex() + 1)
        self.location_label.setText("Manchester, ENG, GB")
        self.time_label.setText(datetime.now(timezone.utc).strftime("%H:%M %Z"))

    def send(self) -> None:
        if self.authentication_service.authenticate(self.stored["user_device_id"]+";"+self.stored["user_phone_number"]):
            if self.code_field.text() == self.code_label.text():
                self.message_service.send(self, "Authenticated", None)
                self.code_field.setEnabled(False)
                self.code_btn.setEnabled(False)
                self.verify_btn.setEnabled(False)
                self.not_login_btn.hide()
            else:
                QMessageBox.warning(self, "Error", "Authentication failed. Try again.")