from typing import Any
from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer
from models.authentication.authentication import Method
from viewmodels.authentication.password_viewmodel import *
from viewmodels.authentication.chip_pin_viewmodel import *
from viewmodels.authentication.security_question_viewmodel import *
from viewmodels.authentication.picture_password_viewmodel import *
from viewmodels.authentication.fingerprint_viewmodel import *
from viewmodels.authentication.totp_viewmodel import *
from viewmodels.authentication.twofa_key_viewmodel import *


class SimulateViewModel(QObject):
    view_creator = pyqtSignal()
    view_registration = pyqtSignal()
    view_authentication = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.message_service = ApplicationContainer.message_service()

        self.message_service.subscribe(self, CreatorViewModel, self.on_message)
        self.message_service.subscribe(self, RegisterViewModel, self.on_message)
        self.message_service.subscribe(self, AuthenticateViewModel, self.on_message)

        self.message_service.send(self, "Update Creator")
    
    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Register View":
            self.view_registration.emit()
        elif message_title == "Authenticate View":
            self.view_authentication.emit()
        elif message_title == "Creator View":
            self.message_service.send(self, "Update Creator")
            self.view_creator.emit()
            

class CreatorViewModel(QObject):
    simulation_changed = pyqtSignal(list, int)

    def __init__(self) -> None:
        super().__init__()

        self.data_service = ApplicationContainer.data_service()
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        # Map type val to string
        self.type_to_string = {
            Method.PASSWORD.value: "Password",
            Method.SECRET_QUESTION.value: "Security Questions",
            Method.PICTURE_PASSWORD.value: "Picture Password",
            Method.FINGERPRINT.value: "Fingerprint Device",
            Method.CHIP_PIN.value: "Chip && PIN",
            Method.TOTP.value: "TOTP",
            Method.TWOFA_KEY.value: "2FA Key"
        }
        self.string_to_type = {v: k for k, v in self.type_to_string.items()}

        self.unlocked_simulations = [(self.type_to_string[k], v) for k, v in self.data_service.get_user_unlocked_simulations().items()]

        self.message_service.subscribe(self, SimulateViewModel, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Update Creator":
            self.authentication_service.reset()
            self.simulation_changed.emit([], 0)

    
    def unlock_simulation(self, method_name: str) -> bool:
        if self.data_service.get_user_coins() >= 200: #coins to unlock the method
            self.data_service.update_user_coin(-200)
            self.data_service.unlock_user_simulation(self.string_to_type[method_name])

            self.message_service.send(self, "Success Notification", "New simulation unlocked.")
            return True
        
        self.message_service.send(self, "Warning Notification", "Please acquire at least 200 coins.")
        return False
    
    def update_simulation(self, method_name: str) -> None:
        method = Method(self.string_to_type[method_name])

        if not self.authentication_service.add(method):
            self.authentication_service.remove(method)
        
        added_types = [self.type_to_string[k.value] for k in self.authentication_service.get_all_types()]
        self.simulation_changed.emit(added_types, self.authentication_service.calculate_assurance_level())
        
    def simulate(self) -> None:
        if self.authentication_service.can_simulate():
            self.message_service.send(self, "Register View")
        else:
            self.message_service.send(self, "Error Notification", "Unable to simulate.")


class RegisterViewModel(QObject):
    reset_signal = pyqtSignal()
    simulation_load = pyqtSignal(object)
    simulation_index_changed = pyqtSignal(int, bool, bool)

    def __init__(self) -> None:
        super().__init__()
        
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.type_to_register = {
            Method.PASSWORD: PasswordRegisterViewModel,
            Method.SECRET_QUESTION: SecurityQuestionRegisterViewModel,
            Method.PICTURE_PASSWORD: PicturePasswordRegisterViewModel,
            Method.FINGERPRINT: FingerprintRegisterViewModel,
            Method.CHIP_PIN: ChipPinRegisterViewModel,
            Method.TOTP: TOTPRegisterViewModel,
            Method.TWOFA_KEY: TwoFAKeyRegisterViewModel
        }
        self.load_index = 0
        
        self.message_service.subscribe(self, CreatorViewModel, self.on_message)

    def on_message(self, message_title: str, *args: Any)  -> None:
        if message_title == "Register View":
            self.load_index = 0
            self.reset_signal.emit()
            self.load_simulation()
        elif message_title == "Registered":
            can_back = self.authentication_service.at > 0
            can_forward = self.authentication_service.at < self.authentication_service.register_count
            self.simulation_index_changed.emit(self.authentication_service.at, can_back, can_forward)

    def load_simulation(self) -> None:
        viewmodel_factory = self.type_to_register.get(self.authentication_service.get_type())
        if viewmodel_factory:
            self.message_service.subscribe(self, viewmodel_factory, self.on_message)
            viewmodel = viewmodel_factory()
            self.simulation_load.emit(viewmodel)
            self.load_index += 1
        else:
            raise ValueError("Unknown authentication method")
        
    def go_forward(self) -> None:
        if not self.authentication_service.go_authenticate():
            if self.authentication_service.forward():
                can_forward = self.authentication_service.at < self.authentication_service.register_count

                if self.authentication_service.at == self.load_index and \
                   self.authentication_service.at == self.authentication_service.register_count:
                    self.load_simulation()

                self.simulation_index_changed.emit(self.authentication_service.at, True, can_forward)  
        else:
            self.message_service.send(self, "Authenticate View")

    def go_backward(self) -> None:
        if self.authentication_service.backward():
            can_back = self.authentication_service.at > 0
            self.simulation_index_changed.emit(self.authentication_service.at, can_back, True)

    def end_simulation(self) -> None:
        self.message_service.send(self, "Creator View")    
        

class AuthenticateViewModel(QObject):
    reset_signal = pyqtSignal()
    simulation_load = pyqtSignal(object)
    simulation_index_changed = pyqtSignal(int, bool, bool)
    bypass_signal = pyqtSignal(int)
    congrats_dialog_signal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.type_to_authenticate = {
            Method.PASSWORD: PasswordAuthenticateViewModel,
            Method.SECRET_QUESTION: SecurityQuestionAuthenticateViewModel,
            Method.PICTURE_PASSWORD: PicturePasswordAuthenticateViewModel,
            Method.FINGERPRINT: FingerprintAuthenticateViewModel,
            Method.CHIP_PIN: ChipPinAuthenticateViewModel,
            Method.TOTP: TOTPAuthenticateViewModel,
            Method.TWOFA_KEY: TwoFAKeyAuthenticateViewModel
        }

        self.load_index = 0

        self.message_service.subscribe(self, RegisterViewModel, self.on_message)

    def on_message(self, message_title: str, *args: Any)  -> None:
        if message_title == "Authenticate View":
            self.reset_signal.emit()
            self.authentication_service.at = 0
            self.load_index = 0
            self.load_simulation()
        if message_title == "Authenticated":
            can_back = self.authentication_service.at > 0
            can_forward = self.authentication_service.at < self.authentication_service.auth_count
            self.simulation_index_changed.emit(self.authentication_service.at, can_back, can_forward)

    def load_simulation(self) -> None:      
        viewmodel_factory = self.type_to_authenticate.get(self.authentication_service.get_type())
        if viewmodel_factory:
            self.message_service.subscribe(self, viewmodel_factory, self.on_message)
            viewmodel = viewmodel_factory()
            self.simulation_load.emit(viewmodel)
            self.load_index += 1
        else:
            raise ValueError("Unknown authentication method")

    def go_forward(self) -> None:
        if not self.authentication_service.go_finish():
            if self.authentication_service.forward():
                can_forward = self.authentication_service.at < self.authentication_service.auth_count

                if self.authentication_service.at == self.load_index and \
                   self.authentication_service.at == self.authentication_service.auth_count:
                    self.load_simulation()

                self.message_service.send(self, "Change View", self.authentication_service.get_type())
                self.simulation_index_changed.emit(self.authentication_service.at, True, can_forward)
        else:
            self.congrats_dialog_signal.emit()

    def go_backward(self) -> None:
        if self.authentication_service.backward():
            can_back = self.authentication_service.at > 0
            self.message_service.send(self, "Change View", self.authentication_service.get_type())
            self.simulation_index_changed.emit(self.authentication_service.at, can_back, True)

    def bypass(self) -> None:
        if self.authentication_service.bypass():
            self.bypass_signal.emit(self.authentication_service.at)

    def end_simulation(self) -> None:
        self.message_service.send(self, "Creator View")

    def complete_simulation(self) -> None:
        self.authentication_service.complete_simulation()
        self.message_service.send(self, "Creator View")
    
        
        
