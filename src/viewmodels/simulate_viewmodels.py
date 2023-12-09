from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from services.container import ApplicationContainer
from models.authentication.authentication import Method
from viewmodels.authentication.password_viewmodel import *
from viewmodels.authentication.pin_viewmodel import *
from viewmodels.authentication.security_question_viewmodel import *
from viewmodels.authentication.image_password_viewmodel import *
from viewmodels.authentication.fingerprint_viewmodel import *
from viewmodels.authentication.push_notification_viewmodel import *
from viewmodels.authentication.twofa_key_viewmodel import *
from widgets.number_button import NumberButton
from models.utils import calculate_assurance_level

# pyright: reportGeneralTypeIssues=false

class SimulateViewModel(QStackedWidget):
    def __init__(self) -> None:
        QStackedWidget.__init__(self)
        self.message_service = ApplicationContainer.message_service()

        # SECTIONS
        self.creator_page = CreatorViewModel()
        self.register_page = RegisterViewModel()
        self.authenticate_page = AuthenticateViewModel()
        self.addWidget(self.creator_page)
        self.addWidget(self.register_page)
        self.addWidget(self.authenticate_page)

        self.message_service.subscribe(self, CreatorViewModel, self.on_message)
        self.message_service.subscribe(self, RegisterViewModel, self.on_message)
        self.message_service.subscribe(self, AuthenticateViewModel, self.on_message)
    
    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Register View":
            self.register_page.setup()
            self.setCurrentWidget(self.register_page)
        elif message_title == "Authenticate View":
            self.authenticate_page.setup()
            self.setCurrentWidget(self.authenticate_page)
        else:
            self.creator_page.setup()
            self.setCurrentWidget(self.creator_page)

class CreatorViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/creator_view.ui", self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.button_container.setAlignment(Qt.AlignRight)

        # Buttons on grid
        self.pin_btn = NumberButton(self, "Pin", QColor(255, 255, 255), QColor(0, 97, 169))
        self.password_btn = NumberButton(self, "Password", QColor(255, 255, 255), QColor(0, 97, 169))
        self.security_questions_btn = NumberButton(self, "Security Questions", QColor(255, 255, 255), QColor(0, 97, 169))
        self.image_password_btn = NumberButton(self, "Image Password", QColor(255, 255, 255), QColor(0, 97, 169))
        self.fingerprint_btn = NumberButton(self, "Fingerprint", QColor(255, 255, 255), QColor(0, 97, 169))
        self.push_notification_btn = NumberButton(self, "Push Notification", QColor(255, 255, 255), QColor(0, 97, 169))
        self.twofa_key_btn = NumberButton(self, "2FA Key", QColor(255, 255, 255), QColor(0, 97, 169))
        self.methods_selection.layout().addWidget(self.pin_btn, 0, 2)
        self.methods_selection.layout().addWidget(self.password_btn, 0, 3)
        self.methods_selection.layout().addWidget(self.security_questions_btn, 0, 4)
        self.methods_selection.layout().addWidget(self.image_password_btn, 1, 2)
        self.methods_selection.layout().addWidget(self.fingerprint_btn, 1, 3)
        self.methods_selection.layout().addWidget(self.push_notification_btn, 1, 4)
        self.methods_selection.layout().addWidget(self.twofa_key_btn, 2, 2)

        # Map type to button
        self.type_to_button = {
            Method.PIN: self.pin_btn,
            Method.PASSWORD: self.password_btn,
            Method.SECRET_QUESTION: self.security_questions_btn,
            Method.IMAGE_PASSWORD: self.image_password_btn,
            Method.FINGER_PRINT: self.fingerprint_btn,
            Method.PUSH_NOTIFICATION: self.push_notification_btn,
            Method.TWOFA_KEY: self.twofa_key_btn
        }

        # Connect buttons to function
        self.pin_btn.clicked.connect(lambda: self.set_method(Method.PIN))
        self.password_btn.clicked.connect(lambda: self.set_method(Method.PASSWORD))
        self.security_questions_btn.clicked.connect(lambda: self.set_method(Method.SECRET_QUESTION))
        self.image_password_btn.clicked.connect(lambda: self.set_method(Method.IMAGE_PASSWORD))
        self.fingerprint_btn.clicked.connect(lambda: self.set_method(Method.FINGER_PRINT))
        self.push_notification_btn.clicked.connect(lambda: self.set_method(Method.PUSH_NOTIFICATION))
        self.twofa_key_btn.clicked.connect(lambda: self.set_method(Method.TWOFA_KEY))

        self.simulate_btn.clicked.connect(self.simulate)

    def setup(self) -> None:
        self.authentication_service.reset()
        self.pin_btn.setChecked(False)
        self.password_btn.setChecked(False)
        self.security_questions_btn.setChecked(False)
        self.image_password_btn.setChecked(False)
        self.fingerprint_btn.setChecked(False)
        self.push_notification_btn.setChecked(False)
        self.twofa_key_btn.setChecked(False)
        self.measure_title.setText("Select challenges from above to see Authenticator Assurance Level")
        self.measure_description.setText("")

    def set_method(self, type: Method) -> None:
        if not self.authentication_service.add(type):
            self.authentication_service.remove(type)
        
        for btn in self.type_to_button.values():
            btn.update_icon(0)

        added_types = self.authentication_service.get_all_types()
        for i in range(len(added_types)):
            self.type_to_button[added_types[i]].update_icon(i+1)
    
        measure = calculate_assurance_level(self.authentication_service.get_all_types())
        if measure:
            title, description = measure.split("|")
            self.measure_title.setText(title)
            self.measure_description.setText(description)
        else:
            self.measure_title.setText("Select challenges from above to see Authenticator Assurance Level")
            self.measure_description.setText("")
        
    def simulate(self) -> None:
        if self.authentication_service.can_simulate():
            self.message_service.send(self, "Register View", None)
        else:
            print("Cannote Simulate.")


class RegisterViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/register_view.ui", self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.type_to_register = {
            Method.PIN: PinRegisterViewModel,
            Method.PASSWORD: PasswordRegisterViewModel,
            Method.SECRET_QUESTION: SecurityQuestionRegisterViewModel,
            Method.IMAGE_PASSWORD: ImagePasswordRegisterViewModel,
            Method.FINGER_PRINT: FingerPrintRegisterViewModel,
            Method.PUSH_NOTIFICATION: PushNotificationRegisterViewModel,
            Method.TWOFA_KEY: TwoFAKeyRegisterViewModel
        }
            
        self.next_btn.clicked.connect(self.go_forward)
        self.back_btn.clicked.connect(self.go_backward)
        self.end_btn.clicked.connect(lambda: self.message_service.send(self, "Creator View", None))

    def setup(self) -> None:
        self.clear_stack()
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.authentication_service.at = 0
        for method in self.authentication_service.get_all_types():
            viewmodel_factory = self.type_to_register.get(method)
            
            if viewmodel_factory:
                self.message_service.subscribe(self, viewmodel_factory, self.on_message)
                self.stackedWidget.addWidget(viewmodel_factory())
            else:
                raise ValueError("Unknown authentication method")

    def on_message(self, message_title: str, *args: Any)  -> None:
        if message_title == "Registered":
            self.next_btn.setEnabled(True)

    def clear_stack(self) -> None:
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(0)
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()

    def go_forward(self) -> None:
        if not self.authentication_service.all_registered():
            self.authentication_service.forward()
            self.stackedWidget.setCurrentIndex(self.authentication_service.at)     
            if self.authentication_service.at == self.authentication_service.register_count:
                self.next_btn.setEnabled(False)
            self.back_btn.setEnabled(True)
        else:
            self.message_service.send(self, "Authenticate View", None)

    def go_backward(self) -> None:
        self.authentication_service.backward()
        self.stackedWidget.setCurrentIndex(self.authentication_service.at)     
        if self.authentication_service.at == 0:
            self.back_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        

class AuthenticateViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/authenticate_view.ui", self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.type_to_authenticate = {
            Method.PIN: PinAuthenticateViewModel,
            Method.PASSWORD: PasswordAuthenticateViewModel,
            Method.SECRET_QUESTION: SecurityQuestionAuthenticateViewModel,
            Method.IMAGE_PASSWORD: ImagePasswordAuthenticateViewModel,
            Method.FINGER_PRINT: FingerPrintAuthenticateViewModel,
            Method.PUSH_NOTIFICATION: PushNotificationAuthenticateViewModel,
            Method.TWOFA_KEY: TwoFAKeyAuthenticateViewModel
        }

        self.next_btn.clicked.connect(self.go_forward)
        self.back_btn.clicked.connect(self.go_backward)
        self.end_btn.clicked.connect(lambda: self.message_service.send(self, "Creator View", None))
    
    def setup(self) -> None:
        self.clear_stack()
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.authentication_service.at = 0
        for method in self.authentication_service.get_all_types():
            viewmodel_factory = self.type_to_authenticate.get(method)
            
            if viewmodel_factory:
                self.message_service.subscribe(self, viewmodel_factory, self.on_message)
                self.stackedWidget.addWidget(viewmodel_factory())
                self.authentication_service.forward() # setting method interface require forward()
            else:
                raise ValueError("Unknown authentication method")
        self.authentication_service.at = 0

    def clear_stack(self) -> None:
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(0)
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()

    def on_message(self, message_title: str, *args: Any)  -> None:
        if message_title == "Authenticated":
            self.next_btn.setEnabled(True)       

    def go_forward(self) -> None:
        if not self.authentication_service.all_authenticated():
            self.authentication_service.forward()
            self.stackedWidget.setCurrentIndex(self.authentication_service.at)     
            if self.authentication_service.at == self.authentication_service.auth_count:
                self.next_btn.setEnabled(False)
            self.back_btn.setEnabled(True)
        else:
            QMessageBox.information(self, "Congratulation", "You have earned 100 coins.")
            self.message_service.send(self, "Creator View", None)

    def go_backward(self) -> None:
        self.authentication_service.backward()
        self.stackedWidget.setCurrentIndex(self.authentication_service.at)     
        if self.authentication_service.at == 0:
            self.back_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        
        
