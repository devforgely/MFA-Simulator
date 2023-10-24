from typing import Any
import hashlib
from models.authentication.authentication import AuthenticationStrategy, Method

class BaseHashStrategy(AuthenticationStrategy):
    def __init__(self) -> None:
        self.plain_key = ""
        self.secret = ""
        self.data = []

    def register(self, key: str) -> str:
        self.plain_key = key
        self.secret = hashlib.sha256(key.encode()).hexdigest()
        return self.secret

    def authenticate(self, key: str, secret: str) -> bool:
        return hashlib.sha256(key.encode()).hexdigest() == secret
    
    def get_plain_key(self) -> str:
        return self.plain_key
    
    def get_secret(self) -> str:
        return self.secret
    
    def store(self, *args: Any) -> None:
        self.data = list(args)

    def get_stored(self) -> list:
        return self.data

class ImagePasswordStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.type = Method.IMAGE_PASSWORD


class PasswordStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.type = Method.PASSWORD


class PinStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.type = Method.PIN


class SecurityQuestionStrategy(BaseHashStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.type = Method.SECRET_QUESTION
