from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QIntValidator, QPixmap
from widgets.info_panel import InfoMode
from viewmodels.simulate_viewmodels import AuthenticateViewModel
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false

class TOTPRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/register_views/totp_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.qr_signal.connect(self.update_qr)
        self._viewmodel.qr_scan_signal.connect(self.update_phone_screen)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.setup_btn.clicked.connect(self.start_setup)
        self.scan_btn.clicked.connect(self._viewmodel.scan_qr)
        self.link_btn.clicked.connect(self._viewmodel.send)
        self.cancel_btn.clicked.connect(self.cancel)

        self.warning_label.setVisible(False)

        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        self.info_panel.add_client_data("Shared Key", ("Shared Key", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("Shared Key", ("Shared Key", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for scanning of QR code to receive shared key...\n")
        self.info_panel.set_measure_level(65)

    def start_setup(self) -> None:
        self._viewmodel.make_qr()
        self.left_stacked.setCurrentIndex(self.left_stacked.currentIndex() + 1)
        self.phone_container.setCurrentIndex(self.phone_container.currentIndex() + 1)

    def update_qr(self, pixmap: QPixmap) -> None:
        self.qr.setPixmap(pixmap)
        self.qr_section.setPixmap(pixmap)

    def update_phone_screen(self, location: str, time: str, ip: str, user_id: str) -> None:
        self.phone_container.setCurrentIndex(self.phone_container.currentIndex() + 1)
        self.location_label.setText(location)
        self.time_label.setText(time)
        self.device_label.setText(ip)
        self.user_label.setText(user_id)           
    
    def cancel(self) -> None:
        self.left_stacked.setCurrentIndex(0)
        self.phone_container.setCurrentIndex(0)
    
    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            tick_label = QLabel()
            tick_label.setScaledContents(True)
            tick_label.setAlignment(Qt.AlignCenter)
            tick_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH+"tick-circle-filled.svg"))
            layout = QVBoxLayout(self.qr)
            layout.addWidget(tick_label)

            self.link_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
        else:
            self.warning_label.setStyleSheet("color: #d5786c;")
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)


    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

        self.info_panel.update_client_data("Shared Key", ("Shared Key", data["shared_key"]))

        self.info_panel.update_server_data("Shared Key", ("Shared Key", data["shared_key"]))

        self.info_panel.log_text("Client: Initiates the TOTP registration process.")
        self.info_panel.log_text("Server: Generates a unique shared secret key encoded as a QR code along with other registration data.")
        self.info_panel.log_text("Server: Present a QR code for the distribution of the shared key.")
        self.info_panel.log_text("Client: Scans the QR code.")
        self.info_panel.log_text("Authentication app extracts the shared secret key and other registration data encoded within the QR code.")
        self.info_panel.log_text("Registration successful.\n")


class TOTPAuthenticateView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/authenticate_views/totp_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.subscribe(AuthenticateViewModel)
        self._viewmodel.time_changed.connect(self.update_time)
        self._viewmodel.code_changed.connect(self.update_code)
        self._viewmodel.clear_code_signal.connect(self.clear_input)

        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
        self.destroyed.connect(self._viewmodel.clean_up)
    
    def setup_ui(self) -> None:
        self.time_bar.setMaximum(self._viewmodel.step_count)

        self.left_frame.adjust_shadow(40, 40, 2, 0)

        sp_retain = self.time_bar.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.time_bar.setSizePolicy(sp_retain)
        self.time_bar.setVisible(False)

        sp_retain = self.warning_label.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.warning_label.setSizePolicy(sp_retain)
        self.warning_label.setVisible(False)

        self.input_boxes = []
        self.input_count = 0
        self.input_boxes.append(self.code1)
        self.input_boxes.append(self.code2)
        self.input_boxes.append(self.code3)
        self.input_boxes.append(self.code4)
        self.input_boxes.append(self.code5)
        self.input_boxes.append(self.code6)

        for i in range(len(self.input_boxes)):
            self.input_boxes[i].setValidator(QIntValidator())
            self.input_boxes[i].textChanged.connect(lambda text, i=i: self.focus_next_input(i))

        self.code_btn.clicked.connect(self.start_code)
        self.verify_btn.clicked.connect(self.send)

        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data()

        self.info_panel.add_client_data("Shared Key", ("Shared Key", data["shared_key"]), InfoMode.EXPAND)
        self.info_panel.add_client_data("TOTP", "NULL")
        
        self.info_panel.add_server_data("Shared Key", ("Shared Key", data["shared_key"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("Sha1 Hash", ("Sha1 Hash", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("TOTP", "NULL")

        self.info_panel.log_text("Waiting for TOTP...\n")

    def focus_next_input(self, index: int) -> None:
        flag = False
        for i in range(index, len(self.input_boxes)):
            if self.input_boxes[i].text() == "":
                flag = True
                self.input_boxes[i].setFocus()
                break
        
        if not flag:
            for i in range(0, index):
                if self.input_boxes[i].text() == "":
                    self.input_boxes[i].setFocus()
                    break

    def clear_input(self) -> None:
        for input in self.input_boxes:
            input.setText("")
        self.input_boxes[0].setFocus()

    def start_code(self) -> None:
        self.code_btn.setVisible(False)
        self.time_bar.setVisible(True)
        self._viewmodel.start_totp()

    def update_code(self, totp: str, time: str) -> None:
        self.code_label.setText(totp)
        self.time_label.setText(time)
        self.clear_input()

    def update_time(self, val: int) -> None:
        self.time_bar.setValue(val)
        self.time_bar.update()

    def send(self) -> None:
        code = ""
        for input in self.input_boxes:
            code += input.text()

        self._viewmodel.send(code)

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            for input in self.input_boxes:
                input.setEnabled(False)
            self.time_bar.setVisible(False)
            self.verify_btn.setEnabled(False)
            self.warning_label.setStyleSheet("color: #049c84")

        self.warning_label.setText(content)
        self.warning_label.setVisible(True)
    
    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")
          
            self.info_panel.log_text("Authentication app generates TOTP based on the current time and the shared key.")
            self.info_panel.log_text("Client: Enter TOTP and send it to the server.")
            self.info_panel.log_text("Server: Calculate TOTP based on the current time and the shared key then verify user sent TOTP.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text("Authentication app generates TOTP based on the current time and the shared key.")
            self.info_panel.log_text("Client: Enter TOTP and send it to the server.")
            self.info_panel.log_text("Server: Calculate TOTP based on the current time and the shared key then verify user sent TOTP.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

        self.info_panel.update_client_data("TOTP", data["totp_entered"])
        self.info_panel.update_server_data("Sha1 Hash", ("Sha1 Hash", data["sha1_hash"]))
        self.info_panel.update_server_data("TOTP", data["totp"])

    def bypass(self) -> None:
        self._viewmodel.bypass()
        self.update_state("The user has been authenticated.", 0)