from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from widgets.info_panel import InfoMode


class PicturePasswordRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/register_views/picture_password_view.ui") -> None:
        super().__init__(parent)
        self.load_ui(ui)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.refresh_images_signal.connect(self.refresh_images)
        self._viewmodel.select_count_change.connect(self.select_lbl.setText)
        self._viewmodel.select_signal.connect(self.show_image_border)
        self._viewmodel.reset_selection_signal.connect(self.reset)

        self._viewmodel.security_measure_changed.connect(self.info_panel.set_measure_level)
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def load_ui(self, ui) -> None:
        uic.loadUi(ui, self)

    def setup_ui(self) -> None:
        self.visible_check.clicked.connect(self.toggle_border_visibility)
        self.refresh_btn.clicked.connect(self._viewmodel.refresh_images)
        self.reset_btn.clicked.connect(self._viewmodel.reset_selection)
        self.submit_btn.clicked.connect(self._viewmodel.send)

        self.warning_label.setVisible(False)

        layout = self.image_view.layout()
        for i in range(layout.count()):
            border_image_label = layout.itemAt(i).widget()
            border_image_label.clicked.connect(self._viewmodel.on_image_click)

        # inital setup for images on grid layout
        self._viewmodel.refresh_images()

        self.frame.adjust_shadow(30, 50, 2, 2)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        self.info_panel.add_client_data("Images", ("Images in Bytes", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Encryption Key", ("Encryption Key for Images", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("IV", ("Initialization Vector used in CBC", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Images", ("User Images Stored as Shared Secret", "NULL"),  InfoMode.EXPAND)

        self.info_panel.log_text("Sending the pictures to the client from the server's database.")
        self.info_panel.log_text("Waiting for the user to select pictures...\n")
    
    def toggle_border_visibility(self) -> None:
        layout = self.image_view.layout()
        if self.visible_check.isChecked():
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        if widget.image in self._viewmodel.selected_images:
                            widget.show_border()
        else:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        if widget.image in self._viewmodel.selected_images:
                            widget.hide_border()

    def refresh_images(self, images: list) -> None:
        layout = self.image_view.layout()

        for i in range(layout.count()):
            border_image_label = layout.itemAt(i).widget()
            border_image_label.setPixmap(QPixmap(images[i]))
            border_image_label.set_image(images[i])
            border_image_label.hide_border()

    def show_image_border(self, widget: QWidget, show: bool) -> None:
        if show:
            if self.visible_check.isChecked():
                widget.show_border()
        else:
            if self.visible_check.isChecked():
                widget.hide_border()

    def reset(self) -> None:
        layout = self.image_view.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.hide_border()

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.refresh_btn.setEnabled(False)

        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

        self.info_panel.update_client_data("Images", ("Images in Bytes", data["user_images"]))
        self.info_panel.update_client_data("Encryption Key", ("Encryption Key for Images", data["encryption_key"]))
        self.info_panel.update_client_data("IV", ("Initialization Vector used in CBC", data["iv"]))

        self.info_panel.update_server_data("User Images", ("User Images Stored as Shared Secret", data["hashed_secret"]))

        self.info_panel.log_text(f"Client: {len(self._viewmodel.selected_images)} images selected.")
        self.info_panel.log_text("Client: Sending data through a secure communication channel.")
        self.info_panel.log_text("Server: Hashing the images in byte using sha-256.")
        self.info_panel.log_text("Registration successful.\n")


class PicturePasswordAuthenticateView(PicturePasswordRegisterView):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/authenticate_views/picture_password_view.ui") -> None:
        super().__init__(viewmodel, info_panel, parent, ui)

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data(False)

        self.info_panel.add_client_data("Images", ("Images in Bytes", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Signed Challenge", ("Signed Challenge", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Images", ("User Images Stored as Shared Secret", data["hashed_secret"]),  InfoMode.EXPAND)
        self.info_panel.add_server_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("Expected Response", ("Expected Response", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Server: Combining user selected images with decoy images and sent to client.")
        self.info_panel.log_text("Waiting for images...\n")

    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

            self.info_panel.log_text(f"Client: Some images selected.")
            self.info_panel.log_text(f"Client: Request to verify identity.")
            self.info_panel.log_text("Server: Generate nonce and send the challenge to the client.")
            self.info_panel.log_text("Client: Signed challenge by hashing the image data and using sha-256, along with a nonce, to create an HMAC.")
            self.info_panel.log_text("Client: Sending signed challenge to the server across the established communication channel.")
            self.info_panel.log_text("Server: Calculate the expected response and verify against the signed challenge.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text(f"Client: {len(self._viewmodel.selected_images)} images selected.")
            self.info_panel.log_text(f"Client: Request to verify identity.")
            self.info_panel.log_text("Server: Generate nonce and send the challenge to the client.")
            self.info_panel.log_text("Client: Signed challenge by hashing the image data and using sha-256, along with a nonce, to create an HMAC.")
            self.info_panel.log_text("Client: Sending signed challenge to the server across the established communication channel.")
            self.info_panel.log_text("Server: Calculate the expected response and verify against the signed challenge.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

        self.info_panel.update_client_data("Images", ("Images in Bytes", data["images"]))
        self.info_panel.update_client_data("Nonce", ("Nonce for Challenge-Response Protocol", data["nonce"]))
        self.info_panel.update_client_data("Signed Challenge", ("Signed Challenge", data["signed_challenge"]))

        self.info_panel.update_server_data("Nonce", ("Nonce for Challenge-Response Protocol", data["nonce"]))
        self.info_panel.update_server_data("Expected Response", ("Expected Response", data["expected_response"]))

    def bypass(self) -> None:
        self._viewmodel.bypass()
        self.update_state("The user has been authenticated.", 0)
