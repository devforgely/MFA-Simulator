from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout
from PyQt5.QtGui import QColor
from widgets.button import LockableNumberButton
from widgets.dialog import GifDialog
from viewmodels.simulate_viewmodels import *
from views.authentication.chip_pin_view import *
from views.authentication.fingerprint_view import *
from views.authentication.password_view import *
from views.authentication.picture_password_view import *
from views.authentication.security_question_view import *
from views.authentication.totp_view import *
from views.authentication.twofa_key_view import *
from widgets.info_panel import *

# pyright: reportAttributeAccessIssue=false

class SimulateView(QStackedWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)

        self._viewmodel = viewmodel

        # SECTIONS
        self.creator_page = CreatorView(CreatorViewModel(), parent=self)
        self.register_page = RegisterView(RegisterViewModel(), parent=self)
        self.authenticate_page = AuthenticateView(AuthenticateViewModel(), parent=self)
        self.addWidget(self.creator_page)
        self.addWidget(self.register_page)
        self.addWidget(self.authenticate_page)

        self._viewmodel.view_creator.connect(lambda: self.setCurrentWidget(self.creator_page))
        self._viewmodel.view_registration.connect(lambda: self.setCurrentWidget(self.register_page))
        self._viewmodel.view_authentication.connect(lambda: self.setCurrentWidget(self.authenticate_page))

class CreatorView(QWidget):
    def __init__(self, viewmodel, parent: QWidget, ui="views_ui/creator_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self._viewmodel.simulation_changed.connect(self.update_simulation_details)

        self.button_group = {}
        self.max_col = 3

        self.setup_ui()

    def setup_ui(self) -> None:
        # Add buttons to grid
        row = 0
        col = 0
        for method_name, unlocked in self._viewmodel.unlocked_simulations:
            btn = LockableNumberButton(self, method_name, QColor(255, 255, 255), QColor(0, 97, 169), not unlocked)
            btn.clicked.connect(lambda bool, name=method_name, button=btn: self.set_method(name, button))
            self.button_group[method_name] = btn
            self.methods_selection.layout().addWidget(btn, row, col)
            col += 1
            if col == self.max_col:
                col = 0
                row += 1

        self.simulate_btn.clicked.connect(self._viewmodel.simulate)

        self.measure_title.setText("Select challenges from above to see Authenticator Assurance Level")
        self.measure_description.setText("")

    
    def update_simulation_details(self, added_types: list, level: int) -> None:
        # clear button icon
        for btn in self.button_group.values():
            btn.update_icon(0)

        # update button icon index
        for i in range(len(added_types)):
            self.button_group[added_types[i]].update_icon(i+1)
    
        match (level):
            case 1:
                title = "Authenticator Assurance Level 1"
                description = "AAL1 provides some assurance that the claimant controls an authenticator bound to the subscriber's account. AAL1 requires either single-factor or multi-factor authentication using a wide range of available authentication technologies. Successful authentication requires that the claimant prove possession and control of the authenticator through a secure authentication protocol."
                self.measure_frame.setStyleSheet("background-color: #c03d33;")
            case 2:
                title = "Authenticator Assurance Level 2"
                description = "AAL2 provides high confidence that the claimant controls an authenticator(s) bound to the subscriber's account. Proof of possession and control of two different authentication factors is required through secure authentication protocol(s). Approved cryptographic techniques are required at AAL2 and above."
                self.measure_frame.setStyleSheet("background-color: #ff7404;")
            case 3:
                title = "Authenticator Assurance Level 3"
                description = "AAL3 provides very high confidence that the claimant controls authenticator(s) bound to the subscriber's account. Authentication at AAL3 is based on proof of possession of a key through a cryptographic protocol. AAL3 authentication requires a hardware-based authenticator and an authenticator that provides verifier impersonation resistance; the same device may fulfill both these requirements. In order to authenticate at AAL3, claimants are required to prove possession and control of two distinct authentication factors through secure authentication protocol(s). Approved cryptographic techniques are required."
                self.measure_frame.setStyleSheet("background-color: #049c84;")
            case _:
                title = "Select challenges from above to see Authenticator Assurance Level"
                description = ""
                self.measure_frame.setStyleSheet("background-color: #0067c0;")

        self.measure_title.setText(title)
        self.measure_description.setText(description)
        

    def set_method(self, method_name: int, button: LockableNumberButton) -> None:
        if button.isLocked():
            if self._viewmodel.unlock_simulation(method_name):
                button.lock(False)
        else:
            self._viewmodel.update_simulation(method_name)           


class RegisterView(QWidget):
    resized = pyqtSignal()

    def __init__(self, viewmodel, parent: QWidget, ui="views_ui/register_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self._viewmodel.reset_signal.connect(self.clear_stack)
        self._viewmodel.simulation_load.connect(self.add_method_view)
        self._viewmodel.simulation_index_changed.connect(self.update_view)

        self.viewmodel_to_view = {
            PasswordRegisterViewModel: PasswordRegisterView,
            SecurityQuestionRegisterViewModel: SecurityQuestionRegisterView,
            PicturePasswordRegisterViewModel: PicturePasswordRegisterView,
            FingerprintRegisterViewModel: FingerprintRegisterView,
            ChipPinRegisterViewModel: ChipPinRegisterView,
            TOTPRegisterViewModel: TOTPRegisterView,
            TwoFAKeyRegisterViewModel: TwoFAKeyRegisterView
        }

        self.setup_ui()

    def setup_ui(self) -> None:
        self.next_btn.clicked.connect(self._viewmodel.go_forward)
        self.back_btn.clicked.connect(self._viewmodel.go_backward)
        self.end_btn.clicked.connect(self._viewmodel.end_simulation)

    def add_method_view(self, viewmodel) -> None:
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)

        # Check if the view model type exists in the mapping
        if viewmodel.__class__ in self.viewmodel_to_view:
            # Get the corresponding view class from the mapping
            view_class = self.viewmodel_to_view[viewmodel.__class__]

            hbox = QWidget()
            hlayout = QHBoxLayout(hbox)
            info_panel = InfoPanel(InfoMode.REGISTER, self)

            # Create an instance of the view with the view model
            view_instance = view_class(viewmodel, info_panel, self.stackedWidget)

            hlayout.addWidget(view_instance)
            hlayout.addWidget(info_panel)

            # Add the view to the stacked widget with info panel 
            self.stackedWidget.addWidget(hbox)
        else:
            raise ValueError("Unknown authentication method")

    def update_view(self, index: int, can_back: bool, can_forward: bool) -> None:
        self.stackedWidget.setCurrentIndex(index)     
        if can_back:
            self.back_btn.setEnabled(True)
        else:
            self.back_btn.setEnabled(False)

        if can_forward:
            self.next_btn.setEnabled(True)
        else:
            self.next_btn.setEnabled(False)

    
    def clear_stack(self) -> None:
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(self.stackedWidget.count() - 1)
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()


class AuthenticateView(QWidget):
    resized = pyqtSignal()
    
    def __init__(self, viewmodel, parent: QWidget, ui="views_ui/authenticate_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self._viewmodel.reset_signal.connect(self.clear_stack)
        self._viewmodel.simulation_load.connect(self.add_method_view)
        self._viewmodel.simulation_index_changed.connect(self.update_view)
        self._viewmodel.bypass_signal.connect(self.bypass)
        self._viewmodel.congrats_dialog_signal.connect(self.show_congrats_dialog)

        self.viewmodel_to_view = {
            PasswordAuthenticateViewModel: PasswordAuthenticateView,
            SecurityQuestionAuthenticateViewModel: SecurityQuestionAuthenticateView,
            PicturePasswordAuthenticateViewModel: PicturePasswordAuthenticateView,
            FingerprintAuthenticateViewModel: FingerprintAuthenticateView,
            ChipPinAuthenticateViewModel: ChipPinAuthenticateView,
            TOTPAuthenticateViewModel: TOTPAuthenticateView,
            TwoFAKeyAuthenticateViewModel: TwoFAKeyAuthenticateView
        }

        self.setup_ui()

    def setup_ui(self) -> None:
        self.next_btn.clicked.connect(self._viewmodel.go_forward)
        self.back_btn.clicked.connect(self._viewmodel.go_backward)
        self.end_btn.clicked.connect(self._viewmodel.end_simulation)
        self.bypass_btn.clicked.connect(self._viewmodel.bypass)

    def add_method_view(self, viewmodel) -> None:
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.bypass_btn.setEnabled(True)

        # Check if the view model type exists in the mapping
        if viewmodel.__class__ in self.viewmodel_to_view:
            # Get the corresponding view class from the mapping
            view_class = self.viewmodel_to_view[viewmodel.__class__]

            hbox = QWidget()
            hlayout = QHBoxLayout(hbox)
            info_panel = InfoPanel(InfoMode.AUTHENTICATE, self)

            # Create an instance of the view with the view model
            view_instance = view_class(viewmodel, info_panel, self.stackedWidget)

            hlayout.addWidget(view_instance)
            hlayout.addWidget(info_panel)

            # Add the view to the stacked widget with info panel 
            self.stackedWidget.addWidget(hbox)
        else:
            raise ValueError("Unknown authentication method")

    def update_view(self, index: int, can_back: bool, can_forward: bool) -> None:
        self.stackedWidget.setCurrentIndex(index)     
        if can_back:
            self.back_btn.setEnabled(True)
        else:
            self.back_btn.setEnabled(False)
        if can_forward:
            self.next_btn.setEnabled(True)
            self.bypass_btn.setEnabled(False)
        else:
            self.next_btn.setEnabled(False)
            self.bypass_btn.setEnabled(True)

    def clear_stack(self) -> None:
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(self.stackedWidget.count() - 1)
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()

    def bypass(self, index: int) -> None:
        self.bypass_btn.setEnabled(False)
        self.next_btn.setEnabled(True)

        container = self.stackedWidget.widget(index)
        if container:
            method_item = container.layout().itemAt(0)
            if method_item:
                method_item.widget().bypass()

    def show_congrats_dialog(self, ):
        # congratulation dialog
        congrats_dialog = GifDialog(self)
        congrats_dialog.move(0, 0)
        congrats_dialog.show()
        congrats_dialog.destroyed.connect(self._viewmodel.complete_simulation)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

