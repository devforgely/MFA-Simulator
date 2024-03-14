from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QButtonGroup
from PyQt5.QtGui import QPixmap
from widgets.waiting_spinner import QtWaitingSpinner
from widgets.info_panel import InfoMode
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false

class TwoFAKeyRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/register_views/twofa_key_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.key_state_changed.connect(self.connect_device)
        self._viewmodel.allow_fingerprint.connect(self.prepare_fingerprint)
        self._viewmodel.fingerprint_progress.connect(self.update_progress)
        
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)
    
        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp3_btn)
        self.finger_group.addButton(self.fp4_btn)

        self.finger_group.buttonToggled.connect(self._viewmodel.on_finger_changed)
        self.fp3_btn.setChecked(True)

        self.w = QtWaitingSpinner(self.page1)

        self.waiting_label = QLabel("Waiting for security key connection...")

        self.next_btn = QPushButton('Next')
        self.next_btn.setMinimumWidth(100)
        self.next_btn.setMinimumHeight(35)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        
        self.page1.layout().addWidget(self.w)
        self.page1.layout().addWidget(self.waiting_label, alignment=Qt.AlignHCenter)
        self.page1.layout().addWidget(self.next_btn, alignment=Qt.AlignRight)

        self.key_select_frame.hide()
        self.guide_label.hide()
        self.key_name_field.hide()
        self.next_btn.hide()
        self.warning_label.setVisible(False)

        self.w.start()

        self.connect_btn.clicked.connect(self._viewmodel.inject_key)
        self.next_btn.clicked.connect(lambda: self._viewmodel.prepare_fingerprint(self.key_name_field.text()))
        self.security_key.clicked.connect(self._viewmodel.set_fingerprint)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])
        
        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Fingerprint Template", ("Fingerprint Template", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Private Key", ("Private Key", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Key Name", "NULL")
        self.info_panel.add_server_data("User Key Handle", ("Key Handle", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Public Key", ("User Public Key", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting to activate two-FA key and scan fingerprint...\n")
        self.info_panel.set_measure_level(95)

    def connect_device(self) -> None:
        self.connect_btn.hide()
        self.w.stop()
        self.waiting_label.hide()

        self.key_select_frame.show()
        self.guide_label.show()
        self.key_name_field.show()
        self.next_btn.show()

        self.security_key.setCursor(Qt.PointingHandCursor)
        self.info_panel.log_text("Client: 2FA Key powered and activated.\n")

    def prepare_fingerprint(self, allow: bool) -> None:
        if allow:
            self.left_stacked.setCurrentIndex(self.left_stacked.currentIndex() + 1)
        else:
            self.warning_label.setVisible(True)

    def update_progress(self, progress: str) -> None:
        self.fingerprint.setPixmap(QPixmap(f"{Settings.IMAGE_FILE_PATH}fp_{progress}.png"))
 
    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.instruction_label.setStyleSheet("color: #049c84")
        self.instruction_label.setText(content)

    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")
    
        self.info_panel.update_client_data("Fingerprint", ("Fingerprint in bytes", data["user_fingerprint"]))
        self.info_panel.update_client_data("Fingerprint Template", ("User Fingerprint Template",  data["fingerprint_template"]))
        self.info_panel.update_client_data("Private Key", ("Private Key", data["private_key"]))

        self.info_panel.update_server_data("User Key Name", self._viewmodel.key_name)
        self.info_panel.update_server_data("User Key Handle", ("Key Handle", data["key_handle"]))
        self.info_panel.update_server_data("User Public Key", ("User Public Key", data["public_key"]))

        self.info_panel.log_text("Client: 2FA Key powered and activated.")
        self.info_panel.log_text("Client: Fingerprint scanned.")
        self.info_panel.log_text("Client: Converting fingerprint to fingerprint template and store inside 2FA key.")
        self.info_panel.log_text("Security key generating public-private key pair and a key handle that references the private key.")
        self.info_panel.log_text("Client: Sending public key, key handle and key name to the server through a secure communication channel.")
        self.info_panel.log_text("Server: Storing public key, key handle and key name that links to the user.")
        self.info_panel.log_text("Registration successful.\n")


class TwoFAKeyAuthenticateView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/authenticate_views/twofa_key_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.key_state_changed.connect(self.connect_device)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp3_btn)
        self.finger_group.addButton(self.fp4_btn)
        self.finger_group.buttonToggled.connect(self._viewmodel.on_finger_changed)
        self.fp3_btn.setChecked(True)

        self.w = QtWaitingSpinner(self.left_frame)
        self.waiting_label = QLabel("Waiting for security key connection...")

        self.left_frame.layout().addWidget(self.w)
        self.left_frame.layout().addWidget(self.waiting_label, alignment=Qt.AlignHCenter)

        self.key_select_frame.hide()
        self.fingerprint.hide()
        self.instruction_label.hide()
        self.warning_label.setVisible(False)

        self.w.start()

        self.connect_btn.clicked.connect(self._viewmodel.inject_key)
        self.security_key.clicked.connect(self._viewmodel.send)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data(False)

        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Fingerprint Template", ("Fingerprint Template", data["fingerprint_template"]), InfoMode.EXPAND)
        self.info_panel.add_client_data("Similarity Score", "NULL")
        self.info_panel.add_client_data("Private Key", ("Private Key", data["private_key"]), InfoMode.EXPAND)
        self.info_panel.add_client_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Signed Challenge", ("Signed Challenge", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Key Handle", ("Key Handle", data["key_handle"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Public Key", ("User Public Key", data["public_key"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting to activate two-FA key and validate fingerprint...\n")

    def connect_device(self) -> None:
        self.connect_btn.hide()
        self.w.stop()
        self.waiting_label.hide()

        self.key_select_frame.show()
        self.key_name.setText(self._viewmodel.get_key_name())
        self.fingerprint.show()
        self.instruction_label.show()

        self.security_key.setCursor(Qt.PointingHandCursor)
        self.info_panel.log_text("Client: 2FA Key powered and activated.\n")

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")              

            self.info_panel.update_client_data("Nonce", ("Nonce for Challenge-Response Protocol", data["nonce"]))
            self.info_panel.update_client_data("Signed Challenge", ("Signed Challenge", data["signed_challenge"]))

            self.info_panel.update_server_data("Nonce", ("Nonce for Challenge-Response Protocol", data["nonce"]))

            self.info_panel.log_text("Server: Generating challenge and sending challenge along with a key handle to client.")
            self.info_panel.log_text("Client: Scanning Fingerprint.")
            self.info_panel.log_text("Security key converting fingerprint to fingerprint template.")
            self.info_panel.log_text("Security key compares fingerprint template with stored features.")
            self.info_panel.log_text("Features matched.")
            self.info_panel.log_text("The security key retrieves the correct private key based on the key handle.")
            self.info_panel.log_text("Security key signs the challenge.")
            self.info_panel.log_text("Client: Sending the signed challenge to the server.")
            self.info_panel.log_text("Server: Verifing the signed challenge using the stored public key.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication",data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text("Server: Generating challenge and sent challenge along with key handle to client.")
            self.info_panel.log_text("Client: Scanning Fingerprint.")
            self.info_panel.log_text("Security key converting fingerprint to fingerprint template.")
            self.info_panel.log_text("Security key compares fingerprint template with stored features.")
            self.info_panel.log_text("Features unmatched.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")
            
        self.info_panel.update_client_data("Fingerprint", ("Fingerprint", data["fingerprint"]))
        self.info_panel.update_client_data("Similarity Score", data["similarity_score"])
    
    def bypass(self) -> None:
        self._viewmodel.bypass()
