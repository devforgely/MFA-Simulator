from typing import Protocol


class AuthenticationStrategy(Protocol):
    def encrypt_key():
        ...
    
    def authenticate() -> bool:
        ...