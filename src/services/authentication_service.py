from typing import Any, List
from models.authentication.authentication import CompoundAuthentication, Method
from models.authentication.authentication_methods import *

class AuthenticationService():
    def __init__(self, data_service) -> None:
        self.data_service = data_service
        self.strategy = CompoundAuthentication()
        self.at = 0
        self.register_count = 0
        self.auth_count = 0

        self.type_to_strategy = {
            Method.PIN: PinStrategy,
            Method.PASSWORD: PasswordStrategy,
            Method.SECRET_QUESTION: SecurityQuestionStrategy,
            Method.IMAGE_PASSWORD: ImagePasswordStrategy,
            Method.FINGER_PRINT: FingerPrintStrategy,
            Method.TOTP: TOTPStrategy,
            Method.TWOFA_KEY: TwoFAKeyStrategy
        }

    def can_simulate(self) -> bool:
        return len(self.strategy) > 0 and (not self.all_registered() or not self.all_authenticated())
    
    def reset(self) -> None:
        self.strategy = CompoundAuthentication()
        self.at = 0
        self.register_count = 0
        self.auth_count = 0
    
    def get_all_types(self) -> List[Method]:
        return self.strategy.get_all_types()
    
    def all_registered(self) -> bool:
        return len(self.strategy) == self.register_count and self.at == self.register_count - 1
    
    def all_authenticated(self) -> bool:
        bool = len(self.strategy) == self.auth_count and self.at == self.auth_count - 1
        if bool:
            self.data_service.update_user_simulation()
        return bool
    
    def add(self, type: Method) -> bool:
        if type not in self.get_all_types():
            strategy_class = self.type_to_strategy.get(type)
            if strategy_class:
                self.strategy.add(strategy_class())
                return True
        return False

    def remove(self, type: Method) -> bool:
        try:
            index = self.get_all_types().index(type)
            self.strategy.remove(index)
            return True
        except ValueError:
            print("Element not found in the list")
            return False
        
    def forward(self) -> None:
        if self.at < len(self.strategy):
            self.at += 1

    def backward(self) -> None:
        if self.at > 0:
            self.at -= 1

    def register(self, *data: Any) -> bool:
        state = self.strategy.register(self.at, *data)
        if state:
            if self.at == self.register_count:
                self.register_count += 1
            return True
        return False
    
    def authenticate(self, *data: Any) -> bool:
        state = self.strategy.authenticate(self.at, *data)
        if state:
            if self.at == self.auth_count:
                self.auth_count += 1
            return True
        return False
    
    def session_store(self, data: dict):
        self.strategy.store(self.at, data)

    def get_session_stored(self) -> dict:
        return self.strategy.get_stored(self.at)