from PyQt5.QtCore import pyqtSignal
from viewmodels.authentication.authentication_base import *
import random
from models.utils import byte_str

class ChipPinRegisterViewModel(AuthenticationBaseViewModel):
    pin_field_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        self.pin_entered = ""
        self.allow_pin = True

    def generate_pin(self) -> None:
        # Generate a random 6-digit PIN, use more secure pseudo random number generator in real world
        self.pin_field_changed.emit(str(random.randint(100000, 999999)))

    def update_pin_field(self, content: str, char: str) -> None:
        if self.allow_pin:
            if not char:
                self.pin_field_changed.emit("")
            else:
                self.pin_field_changed.emit(content+char)
    
    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["hashed_pin"] = byte_str(data["hashed_pin"])
        data["chip_details"] = str(data["chip_details"])
        data["chip_digital_signature"] = byte_str(data["chip_digital_signature"])
        return data

    def send(self, pin) -> None:
        if not self.pin_entered and len(pin) < 4:
            self.state_change.emit("PIN must be at least 4 digits long.", 1)
        elif not self.pin_entered: #first pin check
            self.pin_entered = pin
            self.pin_field_changed.emit("")
            self.state_change.emit("", 2)
        elif pin != self.pin_entered: # restart the whole process
            self.pin_entered = ""
            self.pin_field_changed.emit("")
            self.state_change.emit("PIN did not match.", 3)
        elif self.authentication_service.register(self.pin_entered):
            self.allow_pin = False
            self.state_change.emit("Account registered and card received.", 0)
            self.state_data_change.emit(self.state_data(), 0)
            self.message_service.send(self, "Registered")
        else:
            self.state_change.emit("Registration Fail", 1)


class ChipPinAuthenticateViewModel(AuthenticationBaseViewModel):
    pin_field_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()

        self.allow_pin = False

    def update_pin_field(self, content: str, char: str) -> None:
        if self.allow_pin:
            if not char:
                self.pin_field_changed.emit("")
            else:
                self.pin_field_changed.emit(content+char)

    def state_data(self, is_finish: bool) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["hashed_pin"] = byte_str(data["hashed_pin"])
        data["chip_details"] = str(data["chip_details"])
        data["chip_digital_signature"] = byte_str(data["chip_digital_signature"])

        if is_finish:
            data["arqc"] = byte_str(data["arqc"])
            data["arpc"] = byte_str(data["arpc"])

        return data

    def send(self, pin: str) -> None:
        flag = self.authentication_service.authenticate(pin)

        if not flag:
            self.allow_pin = False
            self.state_change.emit("The user has been authenticated.", flag)
            self.state_data_change.emit(self.state_data(True), flag)
            self.message_service.send(self, "Authenticated")    
        elif flag == 1:
            self.state_change.emit("Incorrect PIN entered", flag)
            self.state_data_change.emit(self.state_data(False), flag)
        elif flag == 2:
            self.state_change.emit("Locked for 10 seconds.", flag)
            self.state_data_change.emit(self.state_data(False), flag)

    def bypass(self) -> None:
        self.allow_pin = False
        self.state_data_change.emit(self.state_data(True), 0)
