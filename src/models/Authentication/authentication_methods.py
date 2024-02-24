from typing import Any
from models.authentication.authentication import AuthenticationStrategy, Method
import hashlib
import datetime
import rsa
import hmac
import math
import secrets
import time

# For purpose of simulation, the strategy is simplified

class SaltStrategy(AuthenticationStrategy): #Salted Challenge Response Authentication Mechanism
    def __init__(self) -> None:
        self.data = {}

    def hash_secret(self, secret, salt):
        return hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), salt, 100000)
    
    def generate_salt(self, length=16):
        return secrets.token_bytes(length)

    def register(self, shared_secret: str) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        salt = self.generate_salt()
        self.data["salt"] = salt
        self.data["hashed_secret"] = self.hash_secret(shared_secret, salt)

        return True

    def authenticate(self, shared_secret: str) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        
        return self.data["hashed_secret"] == self.hash_secret(shared_secret, self.data["salt"])
    
    def bypass(self) -> None:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
    
    def store(self, data: dict) -> None:
        self.data |= data

    def get_stored(self) -> dict:
        return self.data
    

class CardPinStrategy(SaltStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.CARD_PIN
    
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


class FingerPrintStrategy(SaltStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.FINGERPRINT

class PicturePasswordStrategy(SaltStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PICTURE_PASSWORD


class PasswordStrategy(SaltStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PASSWORD
    
    def register(self, username: str, password: str) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        self.data["user_registered"] = username
        self.data["user_password"] = password # For bypass
        salt = self.generate_salt()
        self.data["salt"] = salt
        self.data["hashed_secret"] = self.hash_secret(f"{username}${password}", salt)
        
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        return username == self.data["user_registered"] \
                and self.hash_secret(f"{username}${password}", self.data["salt"]) == self.data["hashed_secret"]

    
class TOTPStrategy(SaltStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.TOTP
    
    def register(self) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())
        self.data["shared_key"] = secrets.token_hex(16)
        return True
    
    def authenticate(self, key: str) -> bool:
        if key:
            self.data["timestamp_authenticate"] = str(datetime.datetime.now())
            self.data["totp"] = self.generate_TOTP()
            return key == self.data["totp"]
        else:
            self.data["totp"] = self.generate_TOTP()
            return False
    
    def generate_TOTP(self) -> str:
        current_time = time.time()
        time_step = 50 # In seconds
        t = math.floor(current_time / time_step)
        h = hmac.new(
            bytes(self.data["shared_key"], encoding="utf-8"),
            t.to_bytes(length=8, byteorder="big"),
            hashlib.sha1,
        )
        digest = h.hexdigest()
        self.data["sha1_hash"] = digest

        # truncate
        digits = 6
        offset = int(digest[-1], 16)
        binary = int(digest[(offset * 2):((offset * 2) + 8)], 16) & 0x7fffffff
        passcode = binary % 10 ** digits
        return str(passcode).zfill(digits)

class SecurityQuestionStrategy(SaltStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.SECRET_QUESTION
    
    def register(self, questions: list[str], answers: str) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        self.data["user_questions"] = questions
        self.data["user_answers"] = answers # For bypass
        salt = self.generate_salt()
        self.data["salt"] = salt
        self.data["hashed_secret"] = self.hash_secret(answers, salt)
        return True
    
    def authenticate(self, answers: str) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())

        return self.hash_secret(answers, self.data["salt"]) == self.data["hashed_secret"]
    

class TwoFAKeyStrategy(TOTPStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.TWOFA_KEY
