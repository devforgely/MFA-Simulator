from viewmodels.authentication.authentication_base import *
import random
from models.utils import image_byte, byte_str, decode_key
from configuration.app_configuration import Settings


class TwoFAKeyRegisterViewModel(AuthenticationBaseViewModel):
    key_state_changed = pyqtSignal()
    allow_fingerprint = pyqtSignal(bool)
    fingerprint_progress = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        self.key_on = False
        self.key_name = ""
        self.progress = 0
        self.prev_finger = "fp3"
        self.current_finger = ""
    
    def on_finger_changed(self, button, checked) -> None:
        if checked:
            match (button.objectName()):
                case "fp3_btn":
                    self.current_finger = "fp3"
                case "fp4_btn":
                    self.current_finger = "fp4"

    def inject_key(self) -> None:
        self.key_state_changed.emit()

    def prepare_fingerprint(self, key_name) -> None:
        if len(key_name) < 3:
            self.allow_fingerprint.emit(False)
        else:
            self.key_name = key_name
            self.key_on = True
            self.allow_fingerprint.emit(True)

    def set_fingerprint(self) -> None:
        if self.key_on:
            if self.prev_finger != self.current_finger:
                self.progress = 0
                self.prev_finger = self.current_finger
            elif self.progress < 5:
                step = random.choice([1, 2])
                self.progress += step
                if self.progress >= 5:
                    self.progress = 5
                    self.send(self.key_name, Settings.FINGERPRINT_FILE_PATH+self.current_finger+".png")
            self.fingerprint_progress.emit(str(self.progress))
    
    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["user_fingerprint"] = byte_str(data["user_fingerprint"])
        data["fingerprint_template"] = byte_str(data["fingerprint_template"].tobytes())
        data["private_key"] = decode_key(data["private_key"])
        data["public_key"] = decode_key(data["public_key"])
        return data

    def send(self, key_name: str, fingerprint: str) -> None:
        fingerprint_data = image_byte(fingerprint)

        if self.authentication_service.register(fingerprint_data):
            self.key_on = False
            self.authentication_service.session_store({"key_name":key_name})
            self.state_change.emit("Registration Completed", 0)
            self.state_data_change.emit(self.state_data(), 0)
            self.message_service.send(self, "Registered")
        else:
            self.state_change.emit("Registration Fail", 1)
            

class TwoFAKeyAuthenticateViewModel(AuthenticationBaseViewModel):
    key_state_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        self.key_on = False
        self.current_finger = ""

    def get_key_name(self) -> str:
        return self.authentication_service.get_session_stored()["key_name"]

    def on_finger_changed(self, button, checked) -> None:
        if checked:
            match (button.objectName()):
                case "fp3_btn":
                    self.current_finger = "fp3"
                case "fp4_btn":
                    self.current_finger = "fp4"

    def inject_key(self) -> None:
        self.key_on = True
        self.key_state_changed.emit()

    def state_data(self, is_checked: bool) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["fingerprint_template"] = byte_str(data["fingerprint_template"].tobytes())
        data["private_key"] = decode_key(data["private_key"])
        data["public_key"] = decode_key(data["public_key"])
        data["fingerprint"] = byte_str(data["fingerprint"])
        data["similarity_score"] = str(data["similarity_score"])

        if is_checked:
            data["nonce"] = byte_str(data["nonce"])
            data["signed_challenge"] = byte_str(data["signed_challenge"])
            
        return data
        
    def send(self) -> None:
        if self.key_on:
            fingerprint_data = image_byte(Settings.FINGERPRINT_FILE_PATH+self.current_finger+".png")
            flag = self.authentication_service.authenticate(fingerprint_data)

            if not flag:
                self.key_on = False
                self.state_change.emit("The user has been authenticated.", flag)
                self.state_data_change.emit(self.state_data(True), flag)
                self.message_service.send(self, "Authenticated")
            elif flag == 1:
                self.state_change.emit("Your credentials do not match our record.", flag)
                self.state_data_change.emit(self.state_data(False), flag)
            elif flag == 2:
                self.state_change.emit("Locked for 10 seconds.", flag)
                self.state_data_change.emit(self.state_data(False), flag)

    
    def bypass(self) -> None:
        self.state_data_change.emit(self.state_data(True), 0)