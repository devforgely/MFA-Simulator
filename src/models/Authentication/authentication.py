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
    
    def register(self, index: int, *data: Any) -> str:
        ...

    def authenticate(self, index: int, *data: Any) -> bool:
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
    
    def get_type(self) -> Method:
        return Method.COMPOUND
    
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

    def store(self, index: int, data: dict) -> None:
        self.childens[index].store(data)

    def get_stored(self, index: int) -> dict:
        return self.childens[index].get_stored()