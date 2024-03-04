from typing import Any, List
from models.authentication.authentication import CompoundAuthentication, Method
from models.authentication.authentication_methods import *
from data.data_service import Badge
import time

class AuthenticationService():
    def __init__(self, data_service) -> None:
        self.data_service = data_service
        self.strategy = CompoundAuthentication()
        self.measure = 0
        self.at = 0
        self.register_count = 0
        self.auth_count = 0
        self.auth_false_count = 0
        self.lock_time = 0.0
        self.LIMIT_COUNT = 5
        self.LOCK_DURATION = 10

        self.type_to_strategy = {
            Method.PASSWORD: PasswordStrategy,
            Method.SECRET_QUESTION: SecurityQuestionStrategy,
            Method.PICTURE_PASSWORD: PicturePasswordStrategy,
            Method.FINGERPRINT: FingerPrintStrategy,
            Method.CHIP_PIN: ChipPinStrategy,
            Method.TOTP: TOTPStrategy,
            Method.TWOFA_KEY: TwoFAKeyStrategy
        }

        self.type_to_string = {
            Method.PASSWORD: "password",
            Method.SECRET_QUESTION: "security_question",
            Method.PICTURE_PASSWORD: "picture_password",
            Method.FINGERPRINT: "fingerprint",
            Method.CHIP_PIN: "chip_pin",
            Method.TOTP: "totp",
            Method.TWOFA_KEY: "twofa_key"
        }


    def can_simulate(self) -> bool:
        return len(self.strategy) > 0 and (not self.all_registered() or not self.all_authenticated())
    
    def reset(self) -> None:
        self.strategy = CompoundAuthentication()
        self.measure = 0
        self.at = 0
        self.register_count = 0
        self.auth_count = 0
        self.auth_false_count = 0

    def get_type(self) -> Method:
        return self.strategy.get_type(self.at)
    
    def get_all_types(self) -> List[Method]:
        return self.strategy.get_all_types()

    def calculate_assurance_level(self) -> int:
        methods = self.strategy.get_all_types()
        if len(methods) == 0:
            self.measure = 0
            return self.measure

        knowledge_based = {Method.PASSWORD, Method.SECRET_QUESTION, Method.PICTURE_PASSWORD, Method.CHIP_PIN}
        biometric_based = {Method.FINGERPRINT}
        possession_based = {Method.TOTP, Method.CHIP_PIN}

        if Method.TWOFA_KEY in methods:
            self.measure = 3
        elif any(element in knowledge_based for element in methods) \
            + any(element in biometric_based for element in methods) \
            + any(element in possession_based for element in methods) >= 2:
            self.measure = 2
        else:
            self.measure = 1
        return self.measure
    
    def all_registered(self) -> bool:
        return len(self.strategy) == self.register_count
    
    def go_authenticate(self) -> bool:
        return self.all_registered() and self.at == self.register_count - 1
    
    def all_authenticated(self) -> bool:
        return len(self.strategy) == self.auth_count
    
    def go_finish(self) -> bool:
        return self.all_authenticated() and self.at == self.auth_count - 1
    
    def complete_simulation(self) -> None:
        #BADGE CONDITION
        if self.measure == 1:
            self.data_service.update_user_badge(Badge.ONE_FA)
        elif self.measure == 2:
            self.data_service.update_user_badge(Badge.TWO_FA)
        elif self.measure == 3:
            self.data_service.update_user_badge(Badge.MFA)
        #BADGE END
        
        self.data_service.update_user_simulation()
        self.reset()
    
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
            return False
        
    def forward(self) -> bool:
        if self.at < self.register_count or self.at < self.auth_count:
            self.at += 1
            return True
        return False

    def backward(self) -> bool:
        if self.at > 0:
            self.at -= 1
            return True
        return False

    def get_display_details(self) -> dict:
        if not self.all_registered():
            return self.data_service.get_simulation_details(self.type_to_string[self.strategy.get_type(self.at)])["registration"]
        else:
            return self.data_service.get_simulation_details(self.type_to_string[self.strategy.get_type(self.at)])["authentication"]

    def register(self, *data: Any) -> bool:
        state = self.strategy.register(self.at, *data)
        if state:
            if self.at == self.register_count:
                self.register_count += 1
            return True
        return False
    
    def authenticate(self, *data: Any) -> int:
        # 2 for lock
        # 1 for fail
        # 0 for success
        if self.auth_false_count < self.LIMIT_COUNT:
            if time.time() - self.lock_time >= self.LOCK_DURATION:
                state = self.strategy.authenticate(self.at, *data)
                if state:
                    if self.at == self.auth_count:
                        self.auth_count += 1
                    return 0
                
                self.auth_false_count += 1
                return 1
            return 2

        self.lock_time = time.time()
        self.auth_false_count = 0
        return 2
    
    def bypass(self) -> bool:
        if not self.all_authenticated() and self.at == self.auth_count and self.data_service.update_user_coin(-100):
            self.strategy.bypass(self.at)
            if self.at == self.auth_count:
                self.auth_count += 1
            return True
        return False
    
    def session_store(self, data: dict):
        self.strategy.store(self.at, data)

    def get_session_stored(self) -> dict:
        return self.strategy.get_stored(self.at)