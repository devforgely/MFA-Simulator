from typing import Any
import hashlib
import datetime
from models.authentication.authentication import AuthenticationStrategy, Method
import rsa

class BaseHashStrategy(AuthenticationStrategy):
    def __init__(self) -> None:
        self.data = {}

    def get_type(self) -> Method:
        return Method.BASEHASH

    def register(self, key: str) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())
        self.data["key"] = hashlib.sha256(key.encode()).hexdigest()
        return True

    def authenticate(self, key: str) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        return hashlib.sha256(key.encode()).hexdigest() == self.data["key"]
    
    def store(self, data: dict) -> None:
        self.data |= data

    def get_stored(self) -> dict:
        return self.data
    
class FingerPrintStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.FINGER_PRINT

class ImagePasswordStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.IMAGE_PASSWORD


class PasswordStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PASSWORD
    
    def register(self, username: str, password: str) -> bool:
        self.data["user_registered"] = username
        self.data["user_password"] = hashlib.sha256(password.encode()).hexdigest()
        self.data["timestamp_register"] = str(datetime.datetime.now())
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        return username == self.data["user_registered"] and hashlib.sha256(password.encode()).hexdigest() == self.data["user_password"]

class PinStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PIN
    
    def register(self, public_key: bytes) -> bool:
        self.data["public_key"] = public_key
        self.data["timestamp_register"] = str(datetime.datetime.now())

        # prepare for authentication
        self.data["server_challenge"] = ("Approval").encode()

        return True

    def authenticate(self, signature: bytes) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        try:
            rsa.verify(self.data["server_challenge"], signature, rsa.PublicKey.load_pkcs1(self.data["public_key"]))
            return True
        except rsa.VerificationError:
            return False
    
class PushNotificationStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PUSH_NOTIFICATION


class SecurityQuestionStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.SECRET_QUESTION
    

class TwoFAKeyStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.TWOFA_KEY
