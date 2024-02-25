from typing import Protocol, Any, List
from enum import Enum
import datetime

class Method(Enum):
    NULL = 0
    PASSWORD = 1
    SECRET_QUESTION = 2
    PICTURE_PASSWORD = 3
    FINGERPRINT = 4
    CARD_PIN = 5
    TOTP = 6
    TWOFA_KEY = 7


class AuthenticationStrategy(Protocol):
    def get_type(self) -> Method:
        return Method.NULL
    
    def register(self, index: int, *data: Any) -> str:
        ...

    def authenticate(self, index: int, *data: Any) -> bool:
        ...

    def bypass(self) -> None:
        ...

    def store(self, index: int, data: dict) -> None:
        ...

    def get_stored(self, index: int) -> dict:
        ...


class CompoundAuthentication(AuthenticationStrategy):
    def __init__(self) -> None:
        self.childens = []

    def __len__(self) -> int:
        return len(self.childens)
    
    def get_type(self, index: int) -> Method:
        return self.childens[index].get_type()
    
    def get_all_types(self) -> List[Method]:
        return [t.get_type() for t in self.childens]
    
    def add(self, child: AuthenticationStrategy) -> None:
        self.childens.append(child)

    def remove(self, index: int) -> None:
        del self.childens[index]

    def register(self, index: int, *data: Any) -> bool:     
        return self.childens[index].register(*data)

    def authenticate(self, index: int, *data: Any) -> bool:
        return self.childens[index].authenticate(*data)
    
    def bypass(self, index) -> None:
        self.childens[index].bypass()

    def store(self, index: int, data: dict) -> None:
        self.childens[index].store(data)

    def get_stored(self, index: int) -> dict:
        return self.childens[index].get_stored()
    

class BaseStrategy(AuthenticationStrategy):
    def __init__(self) -> None:
        self.data = {}

    def bypass(self) -> None:
        self.data["timestamp_authenticate"] = str(datetime.datetime.now())
    
    def store(self, data: dict) -> None:
        self.data |= data

    def get_stored(self) -> dict:
        return self.data