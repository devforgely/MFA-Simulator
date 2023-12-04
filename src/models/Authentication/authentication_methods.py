from typing import Any
import hashlib
import datetime
from models.authentication.authentication import AuthenticationStrategy, Method

class BaseHashStrategy(AuthenticationStrategy):
    def __init__(self) -> None:
        self.plain_key = ""
        self.secret = ""
        self.timestamp = ""
        self.data = []

    def get_type(self) -> Method:
        return Method.BASEHASH

    def register(self, key: str) -> bool:
        self.plain_key = key
        self.secret = hashlib.sha256(key.encode()).hexdigest()
        self.timestamp = str(datetime.datetime.now())
        return True

    def authenticate(self, key: str) -> bool:
        return hashlib.sha256(key.encode()).hexdigest() == self.secret
    
    def get_plain_key(self) -> str:
        return self.plain_key
    
    def get_secret(self) -> str:
        return self.secret
    
    def get_timestamp(self) -> str:
        return self.timestamp
    
    def store(self, *args: Any) -> None:
        self.data = list(args)

    def get_stored(self) -> list:
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


class PinStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PIN
    
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
