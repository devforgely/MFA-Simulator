from typing import Any
from models.authentication.authentication import BaseStrategy, Method
import hashlib
import datetime
import hmac
import math
import secrets
import time
import random
import uuid
import rsa

# For purpose of simulation, the strategy is simplified

class SaltStrategy(BaseStrategy): # Salted hashing
    def __init__(self) -> None:
        super().__init__()

    def hash_secret(self, secret, salt):
        return hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), salt, 100000)
    
    def generate_salt(self, length=16):
        return secrets.token_bytes(length)
    
class ChipPinStrategy(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.CHIP_PIN
    
    def generate_arqc(self) -> bytes:
        # Simulating ARQC generation
        return hashlib.sha256(str(self.data["chip_details"]).encode() + self.data["chip_digital_signature"] + b"transaction_data").digest()
    
    def generate_arpc(self, arqc: bytes) -> bytes:
        # Simulating ARPC generation
        return hashlib.sha256(str(self.data["chip_details"]).encode() + self.data["chip_digital_signature"] + arqc).digest()
    
    def register(self, pin: str) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        self.data["pin"] = pin #For bypass
        self.data["hashed_pin"] = hashlib.sha256(bytes(pin, "utf-8")).digest()
        self.data["chip_details"] = uuid.uuid4()
        self.data["chip_digital_signature"] = secrets.token_bytes(32)

        return True

    def authenticate(self, pin: str) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())

        # Simulate card verifying PIN against hashed PIN
        if hashlib.sha256(bytes(pin, "utf-8")).digest() == self.data["hashed_pin"]:
            self.data["arqc"] = self.generate_arqc()
            self.data["arpc"] = self.generate_arpc(self.data["arqc"])
            return True
        return False
    
    def bypass(self) -> None:
        self.authenticate(self.data["pin"])

class FingerPrintStrategy(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.FINGERPRINT
    
    def register(self, fingerprint: bytes) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        self.data["fingerprint"] = fingerprint #For bypass

        # Assuming doing fingerprint to fingerprint template
        self.data["fingerprint_template"] = bytes([byte ^ 0xFA for byte in fingerprint])

        return True
    
    def authenticate(self, fingerprint: bytes) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())

        # Assuming doing fingerprint to fingerprint template
        template = bytes([byte ^ 0xFA for byte in fingerprint])

        # Account for False negative
        if template == self.data["fingerprint_template"] and random.random() > 0.2:
            return True
        return False

class PicturePasswordStrategy(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.PICTURE_PASSWORD
    
    def generate_challenge(self, length=16) -> bytes:
        return secrets.token_bytes(length)
    
    def register(self, images: bytes) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        self.data["images"] = images #For bypass
        self.data["hashed_secret"] = hashlib.sha256(images).digest()
        
        return True
    
    def challenge_response(self, images: bytes) -> None:
        # server send challenge
        nonce = self.generate_challenge()
        self.data["nonce"] = nonce

        # client send to server
        image_hash = hashlib.sha256(images).digest()
        signed_challenge =hmac.new(image_hash, nonce, hashlib.sha256).digest()
        self.data["signed_challenge"] = signed_challenge

        # server calculate the expected response
        expected_response = hmac.new(self.data["hashed_secret"], nonce, hashlib.sha256).digest()
        self.data["expected_response"] = expected_response
    
    def authenticate(self, images: bytes) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        self.challenge_response(images)

        return self.data["expected_response"] == self.data["signed_challenge"]
    
    def bypass(self) -> None:
        self.authenticate(self.data["images"])

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
    
    def register(self, request: str) -> bool:
        if not request:
            self.data["shared_key"] = secrets.token_hex(20)
        else:
            self.data["timestamp_register"] = str(datetime.datetime.now())
        
        return True
    
    def authenticate(self, key: str) -> bool:
        if key != "GENERATE":
            self.data["timestamp_authenticate"] = str(datetime.datetime.now())
            self.data["totp"] = self.generate_TOTP()
            return key == self.data["totp"]
        else:
            self.data["totp"] = self.generate_TOTP() # Simulate TOTP generation on the device
            return False
    
    def generate_TOTP(self) -> str:
        current_time = time.time()
        time_step = 30 # In seconds
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
    
    def bypass(self) -> None:
        self.authenticate(self.generate_TOTP())

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
    
class TwoFAKeyStrategy(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
    
    def get_type(self) -> Method:
        return Method.TWOFA_KEY
    
    def generate_challenge(self, length=16) -> bytes:
        return secrets.token_bytes(length)
    
    def challenge_response(self) -> bool:
        # server send challenge
        nonce = self.generate_challenge()
        self.data["nonce"] = nonce

        # security key signs the challenge then client send to server
        signed_challenge = rsa.sign(nonce, self.data["private_key"], 'SHA-256')
        self.data["signed_challenge"] = signed_challenge

        # server calculate the expected response
        try:
            rsa.verify(nonce, signed_challenge, self.data["public_key"])
            return True
        except rsa.VerificationError:
            return False
    
    def register(self, fingerprint: bytes) -> bool:
        self.data["timestamp_register"] = str(datetime.datetime.now())

        self.data["fingerprint"] = fingerprint #For bypass

        # Assuming doing fingerprint to fingerprint template
        self.data["fingerprint_template"] = bytes([byte ^ 0xFA for byte in fingerprint])
        
        self.data["public_key"], self.data["private_key"] = rsa.newkeys(512) # small bits for simulation

        # Key handle to match to correct private key
        self.data["key_handle"] = hashlib.sha256(b'link_to_private_key').hexdigest()

        return True
    
    def authenticate(self, fingerprint: bytes) -> bool:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())

        # Assuming doing fingerprint to fingerprint template
        template = bytes([byte ^ 0xFA for byte in fingerprint])

        # Account for False negative
        if template == self.data["fingerprint_template"] and random.random() > 0.2:
            return self.challenge_response()
        return False
    
    def bypass(self) -> None:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
        self.challenge_response()