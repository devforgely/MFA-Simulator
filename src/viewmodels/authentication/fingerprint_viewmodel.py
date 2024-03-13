from viewmodels.authentication.authentication_base import *
import random
from models.utils import image_byte, byte_str
from configuration.app_configuration import Settings

class FingerprintRegisterViewModel(AuthenticationBaseViewModel):
    fingerprint_progress = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        self.progress = 0
        self.prev_finger = "fp1"
        self.current_finger = ""
    
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
                self.send(Settings.FINGERPRINT_FILE_PATH+self.current_finger+".png")
        self.fingerprint_progress.emit(str(self.progress))

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["user_fingerprint"] = byte_str(data["user_fingerprint"])
        data["fingerprint_template"] = byte_str(data["fingerprint_template"].tobytes())
        return data

    def send(self, fingerprint: str) -> None:
        fingerprint_data = image_byte(fingerprint)

        if self.authentication_service.register(fingerprint_data):
            self.state_change.emit("Fingerprint added", 0)
            self.state_data_change.emit(self.state_data(), 0)
            self.message_service.send(self, "Registered")
        else:
            self.state_change.emit("Registration Fail", 1)
            

class FingerprintAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()
        
        self.display_details = self.authentication_service.get_display_details()
        self.current_finger = ""

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

    def state_data(self, is_checked: bool) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["fingerprint_template"] = byte_str(data["fingerprint_template"].tobytes())

        if is_checked:
            data["fingerprint"] = byte_str(data["fingerprint"])
            data["similarity_score"] = str(data["similarity_score"])
            
        return data

    def send(self) -> None:
        fingerprint_data = image_byte(Settings.FINGERPRINT_FILE_PATH+self.current_finger+".png")

        flag = self.authentication_service.authenticate(fingerprint_data)
        if flag == 0:
            self.state_change.emit("The user has been authenticated.", flag)
            self.message_service.send(self, "Authenticated") 
        elif flag == 1:
            self.state_change.emit("Your credentials does not match our records.", flag)
        elif flag == 2:
            self.state_change.emit("Locked for 10 seconds.", flag)
            
        self.state_data_change.emit(self.state_data(True), flag)

    def bypass(self) -> None:
        self.state_data_change.emit(self.state_data(True), 0)