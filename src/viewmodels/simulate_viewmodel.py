from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QFrame
from services.container import ApplicationContainer
from models.authentication.authentication import Method
from models.authentication.authentication_methods import *
from viewmodels.password_viewmodel import *
from viewmodels.pin_viewmodel import *
from viewmodels.placeholder_viewmodel import *
from viewmodels.security_question_viewmodel import *
from viewmodels.image_password_viewmodel import *

class SimulateViewModel(QFrame):
    def __init__(self) -> None:
        QFrame.__init__(self)
        uic.loadUi("views/simulate_view.ui", self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()
        self.view = QWidget()

        self.type_to_strategy = {
            Method.PIN: lambda: [self.authentication_service.add(PinStrategy()),
                                 self.message_service.subscribe(self, PinRegisterViewModel, self.on_message),
                                 self.message_service.subscribe(self, PinAuthenticateViewModel, self.on_message)],
            Method.PASSWORD: lambda: [self.authentication_service.add(PasswordStrategy()),
                                 self.message_service.subscribe(self, PasswordRegisterViewModel, self.on_message),
                                 self.message_service.subscribe(self, PasswordAuthenticateViewModel, self.on_message)],
            Method.SECRET_QUESTION: lambda: [self.authentication_service.add(SecurityQuestionStrategy()),
                                 self.message_service.subscribe(self, SecurityQuestionRegisterViewModel, self.on_message),
                                 self.message_service.subscribe(self, SecurityQuestionAuthenticateViewModel, self.on_message)],
            Method.IMAGE_PASSWORD: lambda: [self.authentication_service.add(ImagePasswordStrategy()),
                                 self.message_service.subscribe(self, ImagePasswordRegisterViewModel, self.on_message),
                                 self.message_service.subscribe(self, ImagePasswordAuthenticateViewModel, self.on_message)],
        }

        self.type_to_register = {
            Method.PIN: lambda: PinRegisterViewModel(),
            Method.PASSWORD: lambda: PasswordRegisterViewModel(),
            Method.SECRET_QUESTION: lambda: SecurityQuestionRegisterViewModel(),
            Method.IMAGE_PASSWORD: lambda: ImagePasswordRegisterViewModel(),
        }

        self.type_to_authenticate = {
            Method.PIN: lambda: PinAuthenticateViewModel(),
            Method.PASSWORD: lambda: PasswordAuthenticateViewModel(),
            Method.SECRET_QUESTION: lambda: SecurityQuestionAuthenticateViewModel(),
            Method.IMAGE_PASSWORD: lambda: ImagePasswordAuthenticateViewModel(),
        }

        # Connect widget to function
        self.pin_btn.clicked.connect(lambda: self.add_strategy(Method.PIN))
        self.password_btn.clicked.connect(lambda: self.add_strategy(Method.PASSWORD))
        self.security_questions_btn.clicked.connect(lambda: self.add_strategy(Method.SECRET_QUESTION))
        self.memorised_image_btn.clicked.connect(lambda: self.add_strategy(Method.IMAGE_PASSWORD))

        self.simulate_btn.clicked.connect(self.display_method_view)

    def add_strategy(self, type: Method) -> None:
        strategy = self.type_to_strategy.get(type)
        if strategy:
            strategy()
        else:
            raise ValueError("Unknown authentication method")

    def on_message(self, message_title: str, *args: Any)  -> None:
        print(message_title)
        print(args)
        self.display_method_view()

    def display_method_view(self) -> None:
        if self.authentication_service.can_simulate():
            print("start simulate")
            if not self.authentication_service.is_registered():
                viewmodel_factory = self.type_to_register.get(self.authentication_service.get_view_type())
                if viewmodel_factory:
                    view = viewmodel_factory()
                else:
                    raise ValueError("Unknown authentication method")
            else:
                viewmodel_factory = self.type_to_authenticate.get(self.authentication_service.get_view_type())
                if viewmodel_factory:
                    view = viewmodel_factory()
                else:
                    raise ValueError("Unknown authentication method")
                             
            self.replace_view(view)
        else:
            self.replace_view(PlaceHolderViewModel())
    
    def replace_view(self, view: QWidget) -> None:
        self.verticalLayout.removeWidget(self.view)
        self.view.deleteLater()

        self.view = view
        self.verticalLayout.addWidget(self.view)
        self.verticalLayout.update()  # Ensure the layout is updated
        
