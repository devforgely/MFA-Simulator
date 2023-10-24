from typing import Any
from data.data_service import DataService
from models.authentication.authentication import AuthenticationStrategy, CompoundAuthentication, Method

class AuthenticationService():
    def __init__(self, data_service) -> None:
        self.data_service = data_service
        self.strategy = CompoundAuthentication()

    def can_simulate(self) -> bool:
        return len(self.strategy) > 0 and (not self.is_registered() or not self.is_authenticated())

    def get_view_type(self) -> Method:
        return self.strategy.get_type()
    
    def is_registered(self) -> bool:
        return self.strategy.is_all_registered
    
    def is_authenticated(self) -> bool:
        return self.strategy.is_all_authenticated
    
    def add(self, child: AuthenticationStrategy) -> None:
        self.strategy.add(child)
        print("add strategy")

    def register(self, *args: Any) -> str:
        return self.strategy.register(*args)
    
    def authenticate(self, key: str) -> bool:
        secret = self.strategy.get_secret()
        truth = self.strategy.authenticate(key, secret=secret)
        return truth
    
    def session_store(self, *args: Any):
        self.strategy.store(*args)

    def get_session_stored(self) -> list:
        return self.strategy.get_stored()