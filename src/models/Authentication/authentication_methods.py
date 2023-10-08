from authentication import AuthenticationStrategy

class MemorisedImageStrategy(AuthenticationStrategy):
    def encrypt_key(self):
        pass

    def authenticate(self) -> bool:
        return True



class PasswordStrategy(AuthenticationStrategy):
    def encrypt_key(self):
        pass

    def authenticate(self) -> bool:
        return True



class PinStrategy(AuthenticationStrategy):
    def encrypt_key(self):
        pass

    def authenticate(self) -> bool:
        return True



class SecretQuestionStrategy(AuthenticationStrategy):
    def encrypt_key(self):
        pass

    def authenticate(self) -> bool:
        return True

