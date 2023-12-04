from typing import Protocol, Any, List
from enum import Enum

class Method(Enum):
    COMPOUND = -1
    BASEHASH = 0
    PIN = 1
    PASSWORD = 2
    SECRET_QUESTION = 3
    IMAGE_PASSWORD = 4
    FINGER_PRINT = 5
    PUSH_NOTIFICATION = 6
    TWOFA_KEY = 7


class AuthenticationStrategy(Protocol):
    def get_type(self) -> Method:
        ...
    
    def register(self, *keys: str) -> str:
        ...

    def authenticate(self, *keys: str) -> bool:
        ...

    def get_plain_key(self) -> str:
        ...

    def get_secret(self) -> str:
        ...

    def store(self, *args: Any) -> None:
        ...

    def get_stored(self) -> list:
        ...


class CompoundAuthentication(AuthenticationStrategy):
    def __init__(self) -> None:
        self.childens = []

    def __len__(self) -> int:
        return len(self.childens)
    
    def get_type(self) -> Method:
        return Method.COMPOUND
    
    def get_all_types(self) -> List[Method]:
        return [t.get_type() for t in self.childens]
    
    def add(self, child: AuthenticationStrategy) -> None:
        self.childens.append(child)

    def remove(self, index: int) -> None:
        del self.childens[index]

    def register(self, index: int, *args: Any) -> bool:     
        return self.childens[index].register(*args)

    def authenticate(self, index: int, key: str) -> bool:
        return self.childens[index].authenticate(key)
    
    def get_plain_key(self, index: int) -> str:
        return self.childens[index].get_plain_key()
        
    def get_secret(self, index: int) -> str:
        return self.childens[index].get_secret()
    
    def get_timestamp(self, index: int) -> str:
        return self.childens[index].get_timestamp()

    def store(self, index: int, *args: Any) -> None:
        self.childens[index].store(*args)

    def get_stored(self, index: int) -> list:
        return self.childens[index].get_stored()