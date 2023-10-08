from typing import Protocol


class AuthenticationStrategy(Protocol):
    def encrypt_key(self):
        ...

    def authenticate(self) -> bool:
        ...


class CompoundAuthentication(AuthenticationStrategy):
    def __init__(self) -> None:
        self.childens = []
        self.current_encrypt_index = 0
        self.current_auth_index = 0
    
    def add(self, child) -> None:
        self.childens.append(child)

    def remove(self, child) -> None:
        self.childens.remove(child)

    def encrypt_key(self):
        pass

    def authenticate(self) -> bool:
        return True