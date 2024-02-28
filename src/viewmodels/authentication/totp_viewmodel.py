from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout
from viewmodels.authentication.authentication_base import *
from configuration.app_configuration import Settings
from widgets.timer import TimeThread
from datetime import datetime, timezone
import time
import qrcode
from io import BytesIO
from widgets.info_panel import InfoMode

# pyright: reportAttributeAccessIssue=false

class TOTPRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/totp_view.ui", info_panel)

        self.setup_btn.clicked.connect(self.start_setup)
        self.scan_btn.clicked.connect(self.next_phone_screen)
        self.link_btn.clicked.connect(self.send)
        self.cancel_btn.clicked.connect(self.cancel)

        self.success_label.setVisible(False)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Shared Key", ("Shared Key", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("Shared Key", ("Shared Key", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting for scanning of QR code to receive shared key...\n")
        self.info_panel.set_measure_level(65)

    def start_setup(self) -> None:
        self.left_stacked.setCurrentIndex(self.left_stacked.currentIndex() + 1)
        self.authentication_service.register("")

        qr = qrcode.QRCode()
        qr.add_data(self.authentication_service.get_session_stored()["shared_key"])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        # Create a QPixmap from the BytesIO object
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue(), 'PNG')
        pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)

        self.qr.setPixmap(pixmap)
        self.qr_section.setPixmap(pixmap)
        
        self.next_phone_screen()
    
    def next_phone_screen(self) -> None:
        self.phone_container.setCurrentIndex(self.phone_container.currentIndex() + 1)
        if self.phone_container.currentIndex() == 2:
            self.location_label.setText("Manchester, ENG, GB")
            self.time_label.setText(datetime.now(timezone.utc).strftime("%H:%M %Z"))
            self.device_label.setText("79.195.101.141")
            self.user_label.setText("m91341fa")
    
    def cancel(self) -> None:
        self.left_stacked.setCurrentIndex(0)
        self.phone_container.setCurrentIndex(0)

    def send(self) -> None:
        if self.authentication_service.register("Confirm Key"):
            tick_label = QLabel()
            tick_label.setScaledContents(True)
            tick_label.setAlignment(Qt.AlignCenter)
            tick_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH+"tick-circle-filled.svg"))
            layout = QVBoxLayout(self.qr)
            layout.addWidget(tick_label)

            self.success_label.setVisible(True)
            self.link_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)

            data = self.authentication_service.get_session_stored()
            
            self.info_panel.update_client_status("Registration", data["timestamp_register"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

            self.info_panel.update_client_data("Shared Key", ("Shared Key", data["shared_key"]))

            self.info_panel.update_server_data("Shared Key", ("Shared Key", data["shared_key"]))

            self.info_panel.update_data_note(1)

            self.info_panel.log_text("Client: Initiates the TOTP registration process.")
            self.info_panel.log_text("Server: Generates a unique shared secret key encoded as a QR code along with other registration data.")
            self.info_panel.log_text("Server: Present a QR code for the distribution of the shared key.")
            self.info_panel.log_text("Client: Scans the QR code.")
            self.info_panel.log_text("Authentication app extracts the shared secret key and other registration data encoded within the QR code.")
            self.info_panel.log_text("Registration successful.\n")

            self.message_service.send(self, "Registered", None)

class TOTPAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/totp_view.ui", info_panel)

        # thread for timer
        self.max_time = 30
        self.threading = TimeThread(self.max_time)
        self.threading._signal.connect(self.signal_update)
        self.time_bar.setMaximum(self.threading.MaxValue())

        self.left_frame.adjust_shadow(40, 40, 2, 0)

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
        data = self.authentication_service.get_session_stored()

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

    def start_code(self) -> None:
        self.code_btn.setVisible(False)
        self.get_code()
        self.threading.set_max(int(self.max_time - (time.time() % self.max_time))) # remaining time before totp expire
        self.threading.start()

    def get_code(self) -> None:
        # generate new totp
        self.authentication_service.authenticate("GENERATE")
        totp = self.authentication_service.get_session_stored()["totp"]

        self.code_label.setText(totp)
        
        for input in self.input_boxes:
            input.setText("")
        self.input_boxes[0].setFocus()

        self.time_label.setText(datetime.now(timezone.utc).strftime("%H:%M %Z"))        
        self.time_bar.setVisible(True) 

    def signal_update(self, val: int):
        self.time_bar.setValue(val)
        self.time_bar.update()
        
        if val == 0:
            # Stop the old thread
            if hasattr(self, 'threading'):
                self.threading.quit()
                self.threading.wait()

            self.threading = TimeThread(self.max_time) # Now we are in sync
            self.threading._signal.connect(self.signal_update)
            self.threading.start()
            self.get_code()
            

    def authenticated(self, mode: int = 0) -> None:
        self.threading.stop()
        self.time_bar.setVisible(False)
        
        for input in self.input_boxes:
            input.setEnabled(False)
        
        self.verify_btn.setEnabled(False)
        self.warning_label.setStyleSheet("color: #049c84")
        self.warning_label.setText("The user has been authenticated.")
        self.warning_label.setVisible(True)

        data = self.authentication_service.get_session_stored()

        self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode: #bypass
            self.info_panel.update_client_data("TOTP", data["totp"])
            self.info_panel.update_server_data("Sha1 Hash", ("Sha1 Hash", data["sha1_hash"]))
            self.info_panel.update_server_data("TOTP", data["totp"])

        self.info_panel.log_text("Authentication app generates TOTP based on the current time and the shared key.")
        self.info_panel.log_text("Client: Enter TOTP and send it to the server.")
        self.info_panel.log_text("Server: Calculate TOTP based on the current time and the shared key then verify user sent TOTP.")
        self.info_panel.log_text("Authentication successful.\n")

        self.message_service.send(self, "Authenticated", None)

    def send(self) -> None:
        code = ""
        for input in self.input_boxes:
            code += input.text()

        flag = self.authentication_service.authenticate(code)
        if flag == 0:
            self.authenticated()
        else:
            if flag == 1:
                self.warning_label.setText("The TOTP does not match.")

                self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
                self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Authentication app generates TOTP based on the current time and the shared key.")
                self.info_panel.log_text("Client: Enter TOTP and send it to the server.")
                self.info_panel.log_text("Server: Calculate TOTP based on the current time and the shared key then verify user sent TOTP.")
                self.info_panel.log_text("Authentication unsuccessful.\n")
            elif flag == 2:
                self.warning_label.setText("Locked for 10 seconds.")

                self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

            self.warning_label.setVisible(True)

        data = self.authentication_service.get_session_stored()
        self.info_panel.update_client_data("TOTP", code) 
        self.info_panel.update_server_data("Sha1 Hash", ("Sha1 Hash", data["sha1_hash"]))
        self.info_panel.update_server_data("TOTP", data["totp"])