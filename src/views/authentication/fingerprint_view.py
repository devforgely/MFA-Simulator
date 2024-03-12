from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QButtonGroup
from PyQt5.QtGui import QPixmap, QIcon
from widgets.info_panel import InfoMode
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false

class FingerprintRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/register_views/fingerprint_view.ui", self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.fingerprint_progress.connect(self.update_progress)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp1_btn)
        self.finger_group.addButton(self.fp2_btn)
        self.finger_group.addButton(self.fp3_btn)
        self.finger_group.addButton(self.fp4_btn)
        self.finger_group.addButton(self.fp5_btn)

        self.finger_group.buttonToggled.connect(self._viewmodel.on_finger_changed)
        self.fp1_btn.setChecked(True)

        self.fingerprint_btn.clicked.connect(self._viewmodel.set_fingerprint)

        self.phone_frame.adjust_shadow(40, 60, 5, 5)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Fingerprint Template", ("User Fingerprint Template", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for fingerprint data...\n")
        self.info_panel.set_measure_level(75)
   
    def update_progress(self, progress: str) -> None:
      self.fingerprint_btn.setIcon(QIcon(QPixmap(f"{Settings.IMAGE_FILE_PATH}fp{progress}.png")))
    

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.fingerprint_btn.setEnabled(False)
            self.long_instruction.setText("When you see the fingerprint icon, use your fingerprint to authenticate your identity.")
            self.instruction_label.setText("")
            self.instruction_label.setFixedSize(30, 30)
            self.instruction_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH+"tick-circle-green.svg"))

        self.short_instruction.setText(content)

    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

        self.info_panel.update_client_data("Fingerprint", ("Fingerprint in bytes", data["user_fingerprint"]))

        self.info_panel.update_server_data("User Fingerprint Template", ("User Fingerprint Template", data["fingerprint_template"]))

        self.info_panel.log_text("Client: Fingerprint scanned.")
        self.info_panel.log_text("Client: Sending data through a secure communication channel.")
        self.info_panel.log_text("Server: Converting fingerprint into fingerprint template.")
        self.info_panel.log_text("Server: Securely store the fingerprint template.")
        self.info_panel.log_text("Registration successful.\n")


class FingerprintAuthenticateView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/authenticate_views/fingerprint_view.ui", self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.finger_group = QButtonGroup(self)
        self.finger_group.addButton(self.fp1_btn)
        self.finger_group.addButton(self.fp2_btn)
        self.finger_group.addButton(self.fp3_btn)
        self.finger_group.addButton(self.fp4_btn)
        self.finger_group.addButton(self.fp5_btn)

        self.finger_group.buttonToggled.connect(self._viewmodel.on_finger_changed)
        self.fp1_btn.setChecked(True)
        self.warning_label.setVisible(False)
        self.fingerprint_btn.clicked.connect(self._viewmodel.send)

        self.phone_frame.adjust_shadow(40, 60, 5, 5)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data(False)

        self.info_panel.add_client_data("Fingerprint", ("Fingerprint", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Fingerprint Template", ("User Fingerprint Template", data["fingerprint_template"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("Similarity Score", "NULL")

        self.info_panel.log_text("Waiting for fingerprint data...\n")

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.fingerprint_btn.setEnabled(False)
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")
                
            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Converting data to fingerprint template.")
            self.info_panel.log_text("Server: Comparing fingerprint features.")
            self.info_panel.log_text("Features matched.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text("Client: Fingerprint scanned.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Converting data to fingerprint template.")
            self.info_panel.log_text("Server: Comparing fingerprint features.")
            self.info_panel.log_text("Features unmatched.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

        self.info_panel.update_client_data("Fingerprint", ("Fingerprint", data["fingerprint"]))
        self.info_panel.update_server_data("Similarity Score", data["similarity_score"])

    def bypass(self) -> None:
        self._viewmodel.bypass()