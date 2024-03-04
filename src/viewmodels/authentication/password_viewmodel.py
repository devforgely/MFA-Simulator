from viewmodels.authentication.authentication_base import *
import string
from models.utils import byte_str

class PasswordRegisterViewModel(AuthenticationBaseViewModel):
    scurity_measure_changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        
    def update_security_level(self, content: str) -> None:
        score = 0
        # Check for length
        if len(content) > 15:
            score += 40
        elif len(content) >= 8:
            score += 20
        elif len(content) >= 6:
            score += 10
        
        if any(c in string.ascii_lowercase for c in content):
            score += 10
        
        if any(c in string.ascii_uppercase for c in content):
            score += 15
        
        if any(c.isdigit() for c in content):
            score += 12

        if any(c in string.punctuation for c in content):
            score += 15

        self.scurity_measure_changed.emit(score)

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["hashed_secret"] = byte_str(data["hashed_secret"])
        data["salt"] = byte_str(data["salt"])
        return data


    def send(self, username: str, password: str, repassword: str) -> None:
        if len(username) < 3 or len(password) < 3:
            self.state_change.emit("Credentials is too short.", 1)
        elif password != repassword:
            self.state_change.emit("Passwords do NOT match.", 1)
        elif self.authentication_service.register(username, password):
            self.state_change.emit("Account has been registered.", 0)
            self.state_data_change.emit(self.state_data(), 0)
            self.message_service.send(self, "Registered")
        else:
            self.state_change.emit("Registration Fail", 1)
        


class PasswordAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()
        
        self.display_details = self.authentication_service.get_display_details()

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["hashed_secret"] = byte_str(data["hashed_secret"])
        data["salt"] = byte_str(data["salt"])
        return data

    def send(self, username: str, password: str) -> None:
        flag = self.authentication_service.authenticate(username, password)
        
        if not flag:
            self.state_change.emit("The user has been authenticated.", flag)
            self.message_service.send(self, "Authenticated")
        elif flag == 1:
            self.state_change.emit("These credentials does not match our records.", flag)
        elif flag == 2:
            self.state_change.emit("Locked for 10 seconds.", flag)
        
        self.state_data_change.emit(self.state_data(), flag)

    def bypass(self) -> None:
        self.state_data_change.emit(self.state_data(), 0)

      