from data.data_service import DataService
from models.Authentication.authentication import CompoundAuthentication


class AuthenticationService():
    def __init__(self) -> None:
        self.data_service = DataService()
        self.strategy = CompoundAuthentication()