from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from widgets.clickables import CustomLineEdit
from widgets.info_panel import InfoMode


class PasswordRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/register_views/password_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.scurity_measure_changed.connect(self.info_panel.set_measure_level)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.username_field = CustomLineEdit("Enter Username", True, 23, "user")
        self.password_field = CustomLineEdit("Create Password", False, 23, "lock")
        self.repassword_field = CustomLineEdit("Confirm Password", False, 23, "lock")

        self.frame.layout().insertWidget(2, self.username_field)
        self.frame.layout().insertWidget(3, self.password_field)
        self.frame.layout().insertWidget(4, self.repassword_field)

        sp_retain = self.warning_label.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.warning_label.setSizePolicy(sp_retain)
        self.warning_label.setVisible(False)

        self.password_field.textChanged.connect(self._viewmodel.update_security_level)
        self.submit_btn.clicked.connect(self.submit)

        self.frame.adjust_shadow(30, 50, 2, 2)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        self.info_panel.add_client_data("Username", "NULL")
        self.info_panel.add_client_data("Password", "NULL")
        
        self.info_panel.add_server_data("User Registered", "NULL")
        self.info_panel.add_server_data("Hashed Secret", ("Hashed Secret", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for username and password...\n")

    def submit(self) -> None:
        self._viewmodel.send(self.username_field.text(), self.password_field.text(), self.repassword_field.text())

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

        self.info_panel.update_client_data("Username", data["user_registered"])
        self.info_panel.update_client_data("Password", data["user_password"])

        self.info_panel.update_server_data("User Registered", data["user_registered"])
        self.info_panel.update_server_data("Hashed Secret", ("Hashed Secret", data["hashed_secret"]))
        self.info_panel.update_server_data("Salt", ("Salt Value", data["salt"]))

        self.info_panel.log_text("Client: Username and password entered.")
        self.info_panel.log_text("Client: Sending data through a secure communication channel.")
        self.info_panel.log_text("Server: Registering username and hashing username + password with salt.")
        self.info_panel.log_text("Registration successful.\n")


class PasswordAuthenticateView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/authenticate_views/password_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.username_field = CustomLineEdit("Enter Username", True, 23, "user")
        self.password_field = CustomLineEdit("Enter Password", False, 23, "lock")
        self.frame.layout().insertWidget(2, self.username_field)
        self.frame.layout().insertWidget(3, self.password_field)

        sp_retain = self.warning_label.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.warning_label.setSizePolicy(sp_retain)
        self.warning_label.setVisible(False)
        
        self.submit_btn.clicked.connect(self.submit)
        self.frame.adjust_shadow(30, 50, 2, 2)

        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data()

        self.info_panel.add_client_data("Username", "NULL")
        self.info_panel.add_client_data("Password", "NULL")
        
        self.info_panel.add_server_data("User Registered", data["user_registered"])
        self.info_panel.add_server_data("Hashed Secret", ("Hashed Secret", data["hashed_secret"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", data["salt"]), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for username and password...\n")

    def submit(self) -> None:
        self._viewmodel.send(self.username_field.text(), self.password_field.text())

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
        else:
            self.password_field.clear()
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

            self.info_panel.log_text("Client: Username and password entered.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Received username and password.")
            self.info_panel.log_text("Server: Hashing and salting the received username + password.")
            self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text("Client: Username and password entered.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Received username and password.")
            self.info_panel.log_text("Server: Hashing and salting the received username + password.")
            self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

        self.info_panel.update_client_data("Username", data["username"])
        self.info_panel.update_client_data("Password", data["password"])

    def bypass(self) -> None:
        self._viewmodel.bypass()