from viewmodels.authentication.authentication_base import *
from widgets.clickables import CustomLineEdit
from widgets.info_panel import InfoMode
from models.utils import byte_str, calculate_security_level

class PasswordRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/password_view.ui", info_panel)

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

        self.password_field.textChanged.connect(self.update_security_level)
        self.submit_btn.clicked.connect(self.send)
        self.initalise_infopanel()

        self.frame.adjust_shadow(30, 50, 2, 2)

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Username", "NULL")
        self.info_panel.add_client_data("Password", "NULL")
        
        self.info_panel.add_server_data("User Registered", "NULL")
        self.info_panel.add_server_data("Hashed Secret", ("Hashed Secret", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for username and password...\n")

    def update_security_level(self) -> None:
        self.info_panel.set_measure_level(calculate_security_level(self.password_field.text()))

    def send(self) -> None:
        if len(self.username_field.text()) < 3 or len(self.password_field.text()) < 3:
            self.warning_label.setText("Credentials is too short.")
            self.warning_label.setVisible(True) 
        elif self.password_field.text() == self.repassword_field.text():
            if self.authentication_service.register(self.username_field.text(), self.password_field.text()):
                self.warning_label.setStyleSheet("color: #049c84")
                self.warning_label.setText("Account has been registered.")
                self.warning_label.setVisible(True)
                self.submit_btn.setEnabled(False)

                data = self.authentication_service.get_session_stored()

                self.info_panel.update_client_status("Registration", data["timestamp_register"])
                self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

                self.info_panel.update_client_data("Username", self.username_field.text())
                self.info_panel.update_client_data("Password", self.password_field.text())

                self.info_panel.update_server_data("User Registered", data["user_registered"])
                self.info_panel.update_server_data("Hashed Secret", ("Hashed Secret", byte_str(data["hashed_secret"])))
                self.info_panel.update_server_data("Salt", ("Salt Value", byte_str(data["salt"])))

                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Client: Username and password entered.")
                self.info_panel.log_text("Client: Sending data through a secure communication channel.")
                self.info_panel.log_text("Server: Registering username and hashing username + password with salt.")
                self.info_panel.log_text("Registration successful.\n")

                self.message_service.send(self, "Registered", None)
        else:
            self.warning_label.setVisible(True) 
            

class PasswordAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/password_view.ui", info_panel)
        
        self.username_field = CustomLineEdit("Enter Username", True, 23, "user")
        self.password_field = CustomLineEdit("Enter Password", False, 23, "lock")
        self.frame.layout().insertWidget(2, self.username_field)
        self.frame.layout().insertWidget(3, self.password_field)

        sp_retain = self.warning_label.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.warning_label.setSizePolicy(sp_retain)
        self.warning_label.setVisible(False)
        
        self.submit_btn.clicked.connect(self.send)
        self.initalise_infopanel()

        self.frame.adjust_shadow(30, 50, 2, 2)

    def initalise_infopanel(self) -> None:
        data = self.authentication_service.get_session_stored()

        self.info_panel.add_client_data("Username", "NULL")
        self.info_panel.add_client_data("Password", "NULL")
        
        self.info_panel.add_server_data("User Registered", data["user_registered"])
        self.info_panel.add_server_data("Hashed Secret", ("Hashed Secret", byte_str(data["hashed_secret"])), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", byte_str(data["salt"])), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for username and password...\n")

    def authenticated(self, mode: int = 0) -> None:
        self.warning_label.setStyleSheet("color: #049c84")
        self.warning_label.setText("The user has been authenticated.")
        self.warning_label.setVisible(True)
        self.submit_btn.setEnabled(False)

        data = self.authentication_service.get_session_stored()

        self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode: # bypass mode
            self.info_panel.update_client_data("Username", data["user_registered"])
            self.info_panel.update_client_data("Password", data["user_password"])

        self.info_panel.log_text("Client: Username and password entered.")
        self.info_panel.log_text("Client: Sending data through a secure communication channel.")
        self.info_panel.log_text("Server: Received username and password.")
        self.info_panel.log_text("Server: Hashing and salting the received username + password.")
        self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
        self.info_panel.log_text("Authentication successful.\n")

        self.message_service.send(self, "Authenticated", None)

    def send(self) -> None:
        username = self.username_field.text()
        password = self.password_field.text()
        
        flag = self.authentication_service.authenticate(username, password)
        if flag == 0:
            self.authenticated()
        else:
            self.password_field.clear()
            
            if flag == 1:
                self.warning_label.setText("These credentials does not match our records.")

                self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
                self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Client: Username and password entered.")
                self.info_panel.log_text("Client: Sending data through a secure communication channel.")
                self.info_panel.log_text("Server: Received username and password.")
                self.info_panel.log_text("Server: Hashing and salting the received username + password.")
                self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
                self.info_panel.log_text("Authentication unsuccessful.\n")
            elif flag == 2:
                self.warning_label.setText("Locked for 10 seconds.")

                self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

            self.warning_label.setVisible(True)

        self.info_panel.update_client_data("Username", username)
        self.info_panel.update_client_data("Password", password)