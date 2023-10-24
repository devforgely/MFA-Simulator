from typing import Protocol, Any
from enum import Enum

class Method(Enum):
    PIN = 0
    PASSWORD = 1
    SECRET_QUESTION = 2
    IMAGE_PASSWORD = 3


class AuthenticationStrategy(Protocol):
    def register(self, *keys: str) -> str:
        ...

    def authenticate(self, *keys: str, secret: str) -> bool:
        ...


class CompoundAuthentication(AuthenticationStrategy):
    def __init__(self) -> None:
        self.childens = []
        self.current_register_index = 0
        self.current_auth_index = 0
        self.is_all_registered = False
        self.is_all_authenticated = False

    def __len__(self):
        return len(self.childens)
    
    def add(self, child: AuthenticationStrategy) -> None:
        self.childens.append(child)

    def remove(self, child: AuthenticationStrategy) -> None:
        self.childens.remove(child)

    def get_type(self) -> Method:
        if self.is_all_registered:
            return self.childens[self.current_auth_index].type
        return self.childens[self.current_register_index].type

    def register(self, *args: Any) -> str:
        if not self.is_all_registered:
            secret = self.childens[self.current_register_index].register(*args)
            
            self.current_register_index += 1

            if self.current_register_index == len(self.childens):
                self.is_all_registered = True           
            return secret
        return ""

    def authenticate(self, key: str, secret: str) -> bool:
        if not self.is_all_authenticated:
            truth = self.childens[self.current_auth_index].authenticate(key, secret)
            
            if truth:
                self.current_auth_index += 1
                if self.current_auth_index == len(self.childens):
                    self.is_all_authenticated = True
                return True         
            return False
        return True
    
    def get_plain_key(self) -> str:
        if not self.is_all_registered:
            return self.childens[self.current_register_index].get_plain_key()
        else:
            return self.childens[self.current_auth_index].get_plain_key()
        
    def get_secret(self) -> str:
        if not self.is_all_registered:
            return self.childens[self.current_register_index].get_secret()
        else:
            return self.childens[self.current_auth_index].get_secret()

    def store(self, *args: Any) -> None:    # need to be called before register increments
        self.childens[self.current_register_index].store(*args)

    def get_stored(self) -> list:
        return self.childens[self.current_auth_index].get_stored()