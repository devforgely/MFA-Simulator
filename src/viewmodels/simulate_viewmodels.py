from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout
from PyQt5.QtGui import QColor
from services.container import ApplicationContainer
from models.authentication.authentication import Method
from viewmodels.authentication.password_viewmodel import *
from viewmodels.authentication.card_pin_viewmodel import *
from viewmodels.authentication.security_question_viewmodel import *
from viewmodels.authentication.picture_password_viewmodel import *
from viewmodels.authentication.fingerprint_viewmodel import *
from viewmodels.authentication.totp_viewmodel import *
from viewmodels.authentication.twofa_key_viewmodel import *
from widgets.number_button import LockableNumberButton
from widgets.info_panel import *
from widgets.dialog import GifDialog, DetailViewDialog
from widgets.info_panel import *

# pyright: reportAttributeAccessIssue=false

class SimulateViewModel(QStackedWidget):
    def __init__(self) -> None:
        QStackedWidget.__init__(self)
        self.message_service = ApplicationContainer.message_service()

        # SECTIONS
        self.creator_page = CreatorViewModel()
        self.creator_page.setup()
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
        elif message_title == "Creator View":
            self.creator_page.setup()
            self.setCurrentWidget(self.creator_page)

class CreatorViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/creator_view.ui", self)
        self.data_service = ApplicationContainer.data_service()
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.button_group = {}
        self.max_col = 3
        # Map type val to string
        self.type_to_string = {
            Method.PASSWORD.value: "Password",
            Method.SECRET_QUESTION.value: "Security Questions",
            Method.PICTURE_PASSWORD.value: "Picture Password",
            Method.FINGERPRINT.value: "Fingerprint Device",
            Method.CARD_PIN.value: "Card && Pin",
            Method.TOTP.value: "TOTP",
            Method.TWOFA_KEY.value: "2FA Key"
        }

        # Add buttons to grid
        row = 0
        col = 0
        for method_val, unlocked in self.data_service.get_user_unlocked_simulations().items():
            btn = LockableNumberButton(self, self.type_to_string[method_val], QColor(255, 255, 255), QColor(0, 97, 169), not unlocked)
            btn.clicked.connect(lambda bool, value=method_val, button=btn: self.set_method(value, button))
            self.button_group[method_val] = btn
            self.methods_selection.layout().addWidget(btn, row, col)
            col += 1
            if col == self.max_col:
                col = 0
                row += 1

        self.simulate_btn.clicked.connect(self.simulate)

    def setup(self) -> None:
        self.authentication_service.reset()
        for btn in self.button_group.values():
            btn.update_icon(0)
        
        self.measure_title.setText("Select challenges from above to see Authenticator Assurance Level")
        self.measure_description.setText("")

    def set_method(self, method_val: int, button: LockableNumberButton) -> None:
        if button.isLocked():
            if self.data_service.get_user_coins() >= 200: #coins to unlock the method
                self.data_service.update_user_coin(-200)
                self.data_service.unlock_user_simulation(method_val)
                button.lock(False)
                self.message_service.send(self, "Show Notification", QIcon(Settings.ICON_FILE_PATH+"unlock.svg"), "New simulation unlocked")
            else:
                self.message_service.send(self, "Show Notification", QIcon(Settings.ICON_FILE_PATH+"lock.svg"), "Please acquire at least 200 coins")
        else:
            if not self.authentication_service.add(Method(method_val)):
                self.authentication_service.remove(Method(method_val))
            
            # clear button icon
            for btn in self.button_group.values():
                btn.update_icon(0)

            # update button icon index
            added_types = self.authentication_service.get_all_types()
            for i in range(len(added_types)):
                self.button_group[added_types[i].value].update_icon(i+1)
        
            match (self.authentication_service.calculate_assurance_level()):
                case 1:
                    measure = """Authenticator Assurance Level 1|AAL1 provides some assurance that the claimant controls an authenticator bound to the subscriber's account. AAL1 requires either single-factor or multi-factor authentication using a wide range of available authentication technologies. Successful authentication requires that the claimant prove possession and control of the authenticator through a secure authentication protocol."""
                case 2:
                    measure = """Authenticator Assurance Level 2|AAL2 provides high confidence that the claimant controls an authenticator(s) bound to the subscriber's account. Proof of possession and control of two different authentication factors is required through secure authentication protocol(s). Approved cryptographic techniques are required at AAL2 and above."""
                case 3:
                    measure = """Authenticator Assurance Level 3|AAL3 provides very high confidence that the claimant controls authenticator(s) bound to the subscriber's account. Authentication at AAL3 is based on proof of possession of a key through a cryptographic protocol. AAL3 authentication requires a hardware-based authenticator and an authenticator that provides verifier impersonation resistance; the same device may fulfill both these requirements. In order to authenticate at AAL3, claimants are required to prove possession and control of two distinct authentication factors through secure authentication protocol(s). Approved cryptographic techniques are required."""
                case _:
                    measure = ""

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
            self.message_service.send(self, "Show Notification", QIcon(Settings.ICON_FILE_PATH+"alert-triangle.svg"), "Unable to simulate")


class RegisterViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/register_view.ui", self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.detail_dialog = None

        self.type_to_register = {
            Method.PASSWORD: PasswordRegisterViewModel,
            Method.SECRET_QUESTION: SecurityQuestionRegisterViewModel,
            Method.PICTURE_PASSWORD: PicturePasswordRegisterViewModel,
            Method.FINGERPRINT: FingerPrintRegisterViewModel,
            Method.CARD_PIN: CardPinRegisterViewModel,
            Method.TOTP: TOTPRegisterViewModel,
            Method.TWOFA_KEY: TwoFAKeyRegisterViewModel
        }
            
        self.next_btn.clicked.connect(self.go_forward)
        self.back_btn.clicked.connect(self.go_backward)
        self.end_btn.clicked.connect(lambda: self.message_service.send(self, "Creator View", None))

        self.message_service.subscribe(self, InfoPanel, self.on_message)

    def setup(self) -> None:
        self.clear_stack()
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.authentication_service.at = 0
        for method in self.authentication_service.get_all_types():
            viewmodel_factory = self.type_to_register.get(method)
            
            if viewmodel_factory:
                self.message_service.subscribe(self, viewmodel_factory, self.on_message)
                hbox = QWidget()
                hlayout = QHBoxLayout(hbox)
                info_panel = InfoPanel(self.authentication_service.get_display_details(), 0, hbox)
                
                hlayout.addWidget(viewmodel_factory(info_panel))
                hlayout.addWidget(info_panel) 
                self.stackedWidget.addWidget(hbox)
                self.authentication_service.forward()
            else:
                raise ValueError("Unknown authentication method")
        self.authentication_service.at = 0
        

    def on_message(self, message_title: str, *args: Any)  -> None:
        if message_title == "Registered":
            self.next_btn.setEnabled(True)
        elif message_title == "Register Show Details":
            self.detail_dialog = DetailViewDialog(args[0], args[1], self)
            self.detail_dialog.move(0, 0)
            self.detail_dialog.show()
            self.detail_dialog.destroyed.connect(self.on_detail_dialog_destroyed)

    def clear_stack(self) -> None:
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(self.stackedWidget.count() - 1)
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()

    def go_forward(self) -> None:
        if not self.authentication_service.go_authenticate():
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

    def on_detail_dialog_destroyed(self):
        self.detail_dialog = None

    def resizeEvent(self, event):
        if self.detail_dialog is not None:
            self.detail_dialog.resize(self.size())
        super(RegisterViewModel, self).resizeEvent(event)
        

class AuthenticateViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/authenticate_view.ui", self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.congrats_dialog = None
        self.detail_dialog = None

        self.type_to_authenticate = {
            Method.PASSWORD: PasswordAuthenticateViewModel,
            Method.SECRET_QUESTION: SecurityQuestionAuthenticateViewModel,
            Method.PICTURE_PASSWORD: PicturePasswordAuthenticateViewModel,
            Method.FINGERPRINT: FingerPrintAuthenticateViewModel,
            Method.CARD_PIN: CardPinAuthenticateViewModel,
            Method.TOTP: TOTPAuthenticateViewModel,
            Method.TWOFA_KEY: TwoFAKeyAuthenticateViewModel
        }

        self.next_btn.clicked.connect(self.go_forward)
        self.back_btn.clicked.connect(self.go_backward)
        self.end_btn.clicked.connect(lambda: self.message_service.send(self, "Creator View", None))
        self.bypass_btn.clicked.connect(self.bypass)

        self.message_service.subscribe(self, InfoPanel, self.on_message)
    
    def setup(self) -> None:
        self.clear_stack()
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.authentication_service.at = 0
        for method in self.authentication_service.get_all_types():
            viewmodel_factory = self.type_to_authenticate.get(method)
            
            if viewmodel_factory:
                self.message_service.subscribe(self, viewmodel_factory, self.on_message)
                hbox = QWidget()
                hlayout = QHBoxLayout(hbox)
                info_panel = InfoPanel(self.authentication_service.get_display_details(), 1, hbox)
                
                hlayout.addWidget(viewmodel_factory(info_panel))
                hlayout.addWidget(info_panel)
                self.stackedWidget.addWidget(hbox)
                
                self.authentication_service.forward()
            else:
                raise ValueError("Unknown authentication method")
        self.authentication_service.at = 0

    def clear_stack(self) -> None:
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(self.stackedWidget.count() - 1)
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()

    def on_message(self, message_title: str, *args: Any)  -> None:
        if message_title == "Authenticated":
            self.next_btn.setEnabled(True)
        elif message_title == "Authenticate Show Details":
            self.detail_dialog = DetailViewDialog(args[0], args[1], self)
            self.detail_dialog.move(0, 0)
            self.detail_dialog.show()
            self.detail_dialog.destroyed.connect(self.on_detail_dialog_destroyed)

    def go_forward(self) -> None:
        if not self.authentication_service.go_finish():
            self.authentication_service.forward()
            self.stackedWidget.setCurrentIndex(self.authentication_service.at)     
            if self.authentication_service.at == self.authentication_service.auth_count:
                self.next_btn.setEnabled(False)
                self.bypass_btn.setEnabled(True)
            self.back_btn.setEnabled(True)
            
        else:
            # congratulation dialog
            self.congrats_dialog = GifDialog(self.authentication_service.complete_simulation, self)
            self.congrats_dialog.move(0, 0)
            self.congrats_dialog.show()
            self.congrats_dialog.destroyed.connect(self.on_congrats_dialog_destroyed)

    def go_backward(self) -> None:
        self.authentication_service.backward()
        self.stackedWidget.setCurrentIndex(self.authentication_service.at)     
        if self.authentication_service.at == 0:
            self.back_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        self.bypass_btn.setEnabled(False)

    def bypass(self) -> None:
        if self.authentication_service.bypass():
            container = self.stackedWidget.widget(self.authentication_service.at)
            if container:
                method_item = container.layout().itemAt(0)
                if method_item:
                    method_item.widget().authenticated(1)


    def on_congrats_dialog_destroyed(self):
        self.congrats_dialog = None
        self.message_service.send(self, "Creator View", None)

    def on_detail_dialog_destroyed(self):
        self.detail_dialog = None

    def resizeEvent(self, event):
        if self.congrats_dialog is not None:
            self.congrats_dialog.resize(self.size())
        if self.detail_dialog is not None:
            self.detail_dialog.resize(self.size())
        super(AuthenticateViewModel, self).resizeEvent(event)
        
        
