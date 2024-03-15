from PyQt5 import uic
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap
from configuration.app_configuration import Settings
from widgets.info_panel import InfoMode

# pyright: reportAttributeAccessIssue=false

class ButtonHoverWatcher(QObject):
    def __init__(self, button, default_image: str, hover_image: str)-> None:
        super().__init__(button)
        self.button = button
        self.default_icon = default_image
        self.hover_icon = hover_image

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Enter:
            # The push button is hovered by mouse
            self.button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}{self.hover_icon}.svg"))
        elif event.type() == QEvent.Leave:
            # The push button is not hovered by mouse
            self.button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}{self.default_icon}.svg"))
        return super().eventFilter(watched, event)

class ChipPinRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/register_views/chip_pin_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.pin_field_changed.connect(self.pin_field.setText)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.generate_pin_btn.clicked.connect(self._viewmodel.generate_pin)

        self.btn0.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "0"))
        self.btn1.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "1"))
        self.btn2.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "2"))
        self.btn3.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "3"))
        self.btn4.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "4"))
        self.btn5.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "5"))
        self.btn6.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "6"))
        self.btn7.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "7"))
        self.btn8.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "8"))
        self.btn9.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "9"))
        self.clear_btn.clicked.connect(lambda: self._viewmodel.update_pin_field("", ""))
        self.submit_btn.clicked.connect(lambda: self._viewmodel.send(self.pin_field.text()))

        self.clear_btn.installEventFilter(ButtonHoverWatcher(self.clear_btn, "delete", "delete-red"))
        self.submit_btn.installEventFilter(ButtonHoverWatcher(self.submit_btn, "tick-circle", "tick-circle-green"))

        self.warning_label.setVisible(False)
        self.frame.adjust_shadow(30, 50, 2, 2)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        self.info_panel.add_client_data("Pin", "NULL")
        self.info_panel.add_client_data("Chip Store of Hashed Pin", ("Chip Store of Hashed Pin", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Chip Details", ("Chip Details in Bytes", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Chip Digital Signature", ("Chip Digital Signature", "NULL"), InfoMode.EXPAND)

        self.info_panel.add_server_data("User Chip Details", ("User Chip Details in Bytes", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Chip Digital Signature", ("User Chip Digital Signature", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.log_text("Waiting to create a new chip card and assign a pin...\n")
        self.info_panel.set_measure_level(90)

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.chip_card.setPixmap(QPixmap(Settings.IMAGE_FILE_PATH+"chip_card.png"))
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
        elif flag == 2: # re-enter pin mode
            self.pin_field.setPlaceholderText("Re-Enter PIN")
            self.pin_field.setEchoMode(QLineEdit.Password)
            self.generate_pin_btn.setEnabled(False)
        elif flag == 3:
            self.pin_field.setPlaceholderText("Choose PIN")
            self.pin_field.setEchoMode(QLineEdit.Normal)
            self.generate_pin_btn.setEnabled(True)  

        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

        self.info_panel.update_client_data("Pin", data["user_pin"])
        self.info_panel.update_client_data("Chip Store of Hashed Pin", ("Chip Store of Hashed Pin", data["hashed_pin"]))
        self.info_panel.update_client_data("Chip Details", ("Chip Details in Bytes", data["chip_details"]))
        self.info_panel.update_client_data("Chip Digital Signature", ("Chip Digital Signature", data["chip_digital_signature"]))

        self.info_panel.update_server_data("User Chip Details", ("User Chip Details in Bytes", data["chip_details"]))
        self.info_panel.update_server_data("User Chip Digital Signature", ("User Chip Digital Signature", data["chip_digital_signature"]))

        self.info_panel.log_text("Client: Pin entered.")
        self.info_panel.log_text("Programming hashed pin into the chip, adding chip details and digital signature.")
        self.info_panel.log_text("Server: Storing chip details and digital signature.")
        self.info_panel.log_text("Sending chip to the client.")
        self.info_panel.log_text("Registration successful.\n")


class ChipPinAuthenticateView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/authenticate_views/chip_pin_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.pin_field_changed.connect(self.pin_field.setText)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)
    
        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.chip_card.set_collision(self.terminal)
        self.chip_card.set_collision_call(self.insert_card)

        self.btn0.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "0"))
        self.btn1.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "1"))
        self.btn2.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "2"))
        self.btn3.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "3"))
        self.btn4.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "4"))
        self.btn5.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "5"))
        self.btn6.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "6"))
        self.btn7.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "7"))
        self.btn8.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "8"))
        self.btn9.clicked.connect(lambda: self._viewmodel.update_pin_field(self.pin_field.text(), "9"))
        self.clear_btn.clicked.connect(lambda: self._viewmodel.update_pin_field("", ""))
        self.submit_btn.clicked.connect(lambda: self._viewmodel.send(self.pin_field.text()))

        self.clear_btn.installEventFilter(ButtonHoverWatcher(self.clear_btn, "delete", "delete-red"))
        self.submit_btn.installEventFilter(ButtonHoverWatcher(self.submit_btn, "tick-circle", "tick-circle-green"))
        self.submit_btn.setEnabled(False)
        self.warning_label.setVisible(False)
        self.pin_field.setEchoMode(QLineEdit.Password)
        self.frame.adjust_shadow(30, 50, 2, 2)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data(False)

        self.info_panel.add_client_data("Pin", "NULL")
        self.info_panel.add_client_data("Chip Store of Hashed Pin", ("Chip Store of Hashed Pin", data["hashed_pin"]), InfoMode.EXPAND)
        self.info_panel.add_client_data("Chip Details", ("Chip Details in Bytes", data["chip_details"]), InfoMode.EXPAND)
        self.info_panel.add_client_data("Chip Digital Signature", ("Chip Digital Signature", data["chip_digital_signature"]), InfoMode.EXPAND)
        self.info_panel.add_client_data("ARQC", ("Authorization Request Cryptogram", "NULL"), InfoMode.EXPAND)

        self.info_panel.add_server_data("User Chip Details", ("User Chip Details in Bytes", data["chip_details"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Chip Digital Signature", ("User Chip Digital Signature", data["chip_digital_signature"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("ARPC", ("Authorization Response Cryptogram", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Waiting to insert card then validate pin...\n")

    def insert_card(self) -> None:
        self.terminal.setPixmap(QPixmap(Settings.IMAGE_FILE_PATH+"card_inside.png"))
        if not self.warning_label.isVisible():
            self.pin_field.setPlaceholderText("Enter PIN")
            self._viewmodel.allow_pin = True
            self.submit_btn.setEnabled(True)

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
        else:
            self.pin_field.clear()
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

            self.info_panel.update_client_data("ARQC", ("Authorization Request Cryptogram", data["arqc"]))
            self.info_panel.update_server_data("ARPC", ("Authorization Response Cryptogram", data["arpc"]))

            self.info_panel.log_text("Client: Pin entered.")
            self.info_panel.log_text("Card: Hashing pin and validate against hashed pin stored in the chip.")
            self.info_panel.log_text("Card: Generate ARQC with request detail and digital signature.")
            self.info_panel.log_text("Card: Sending ARQC to the terminal.")
            self.info_panel.log_text("Server: Received ARQC from terminal, verifying ARQC then sending back ARPC.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text("Client: Pin entered.")
            self.info_panel.log_text("Card: Hashing pin and validate against hashed pin stored in the chip.")
            self.info_panel.log_text("Card: The PIN entered does not match in the memory.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

        self.info_panel.update_client_data("Pin", data["pin"])

    def bypass(self) -> None:
        self._viewmodel.bypass()
        self.update_state("The user has been authenticated.", 0)