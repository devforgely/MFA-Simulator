from PyQt5.QtGui import QPixmap
from viewmodels.authentication.authentication_base import *
from widgets.info_panel import InfoMode
import os
import random
from models.utils import images_to_bytes, byte_str


class PicturePasswordRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget, ui="views/register_views/picture_password_view.ui") -> None:
        super().__init__(ui, info_panel)

        self.MAX_SELECT_COUNT = 7

        self.selected_images = []
        self.viewed_images = []

        # Specify the folder path of images
        self.folder_path = 'data/images/'
        # Load images from the folder
        self.images = [self.folder_path+f for f in os.listdir(self.folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

        self.visible_check.clicked.connect(self.toggle_border_visibility)
        self.refresh_btn.clicked.connect(self.refresh_images)
        self.reset_btn.clicked.connect(self.reset)
        self.submit_btn.clicked.connect(self.send)

        self.warning_label.setVisible(False)

        layout = self.image_view.layout()
        for i in range(layout.count()):
            border_image_label = layout.itemAt(i).widget()
            border_image_label.clicked.connect(self.on_image_click)

        # inital setup for images on grid layout
        self.refresh_images()

        self.initalise_infopanel()
        self.frame.adjust_shadow(30, 50, 2, 2)

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Images", ("Images in Bytes", "NULL"), InfoMode.EXPAND)
        
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
                        if widget.image in self.selected_images:
                            widget.show_border()
        else:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        if widget.image in self.selected_images:
                            widget.hide_border()

    def refresh_images(self) -> None:
        random.shuffle(self.images)
        layout = self.image_view.layout()

        # filter over selected images
        temp_images = [x for x in self.images if x not in self.selected_images and x not in self.viewed_images][:9] #copy

        if len(temp_images) < 9:
            random.shuffle(self.viewed_images)
            temp_images.extend(random.sample(self.viewed_images, 9-len(temp_images)))
            self.viewed_images.clear()

        for i in range(layout.count()):
            border_image_label = layout.itemAt(i).widget()
            border_image_label.setPixmap(QPixmap(temp_images[i]))
            border_image_label.set_image(temp_images[i])
            border_image_label.hide_border()

        self.viewed_images.extend(temp_images)

    def on_image_click(self, widget: QWidget) -> None:
        if widget.image in self.selected_images:
            if self.visible_check.isChecked():
                widget.hide_border()
            self.selected_images.remove(widget.image)
        elif len(self.selected_images) < self.MAX_SELECT_COUNT:
            if self.visible_check.isChecked():
                widget.show_border()
            self.selected_images.append(widget.image)
        self.select_lbl.setText(f"Selected Image Count: {len(self.selected_images)}")
        self.info_panel.set_measure_level(len(self.selected_images)*10)

    def reset(self) -> None:
        self.selected_images.clear()
        self.select_lbl.setText("Selected Image Count: 0")
        self.info_panel.set_measure_level(0)

        layout = self.image_view.layout()
        for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.hide_border()

    def send(self) -> None:
        if len(self.selected_images) == 0:
            self.warning_label.setVisible(True)
        else:
            images_byte = images_to_bytes(self.selected_images)

            if self.authentication_service.register(images_byte):
                self.warning_label.setStyleSheet("color: #049c84")
                self.warning_label.setText("Account has been registered.")
                self.warning_label.setVisible(True)
                self.submit_btn.setEnabled(False)

                data = self.authentication_service.get_session_stored()

                self.info_panel.update_client_status("Registration", data["timestamp_register"])
                self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

                self.info_panel.update_client_data("Images", ("Images in Bytes", str(images_byte.hex())))

                self.info_panel.update_server_data("User Images", ("User Images Stored as Shared Secret", byte_str(data["hashed_secret"])))

                self.info_panel.update_data_note(1)

                self.info_panel.log_text(f"Client: {len(self.selected_images)} images selected.")
                self.info_panel.log_text("Client: Sending data through a secure communication channel.")
                self.info_panel.log_text("Server: Hashing the images in byte using sha-256.")
                self.info_panel.log_text("Registration successful.\n")

                self.message_service.send(self, "Registered", None)


class PicturePasswordAuthenticateViewModel(PicturePasswordRegisterViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel, ui="views/authenticate_views/picture_password_view.ui")

    def on_image_click(self, widget: QWidget) -> None:
        if widget.image in self.selected_images:
            if self.visible_check.isChecked():
                widget.hide_border()
            self.selected_images.remove(widget.image)
        elif len(self.selected_images) < self.MAX_SELECT_COUNT:
            if self.visible_check.isChecked():
                widget.show_border()
            self.selected_images.append(widget.image)
        self.select_lbl.setText(f"Selected Image Count: {len(self.selected_images)}")

    def reset(self) -> None:
        self.selected_images.clear()
        self.select_lbl.setText("Selected Image Count: 0")

        layout = self.image_view.layout()
        for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.hide_border()

    def initalise_infopanel(self) -> None:
        data = self.authentication_service.get_session_stored()

        self.info_panel.add_client_data("Images", ("Images in Bytes", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Signed Challenge", ("Signed Challenge", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Images", ("User Images Stored as Shared Secret", byte_str(data["hashed_secret"])),  InfoMode.EXPAND)
        self.info_panel.add_server_data("Nonce", ("Nonce for Challenge-Response Protocol", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("Expected Response", ("Expected Response", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Server: Combining user selected images with decoy images and sent to client.")
        self.info_panel.log_text("Waiting for images...\n")


    def authenticated(self, mode: int = 0) -> None:
        self.warning_label.setStyleSheet("color: #049c84")
        self.warning_label.setText("The user has been authenticated.")
        self.submit_btn.setEnabled(False)

        data = self.authentication_service.get_session_stored()

        self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode:
            self.info_panel.update_client_data("Images", ("Images in Bytes", str(data["images"].hex())))
            self.info_panel.update_client_data("Nonce", ("Nonce for Challenge-Response Protocol", byte_str(data["nonce"])))
            self.info_panel.update_client_data("Signed Challenge", ("Signed Challenge", byte_str(data["signed_challenge"])))

            self.info_panel.update_server_data("Nonce", ("Nonce for Challenge-Response Protocol", byte_str(data["nonce"])))
            self.info_panel.update_server_data("Expected Response", ("Expected Response", byte_str(data["expected_response"])))

        self.info_panel.log_text(f"Client: Some images selected.")
        self.info_panel.log_text(f"Client: Request to verify identity.")
        self.info_panel.log_text("Server: Generate nonce and send the challenge to the client.")
        self.info_panel.log_text("Client: Signed challenge by hashing the image data and using sha-256, along with a nonce, to create an HMAC.")
        self.info_panel.log_text("Client: Sending signed challenge to the server across the established communication channel.")
        self.info_panel.log_text("Server: Calculate the expected response and verify against the signed challenge.")
        self.info_panel.log_text("Authentication successful.\n")

        self.message_service.send(self, "Authenticated", None)

    def send(self) -> None:
        images_byte = images_to_bytes(self.selected_images)

        flag = self.authentication_service.authenticate(images_byte)
        if flag == 0:
            self.authenticated()
        else:
            if flag == 1:
                self.warning_label.setText("These credentials does not match our records.")

                self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
                self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
                self.info_panel.update_data_note(1)

                self.info_panel.log_text(f"Client: {len(self.selected_images)} images selected.")
                self.info_panel.log_text(f"Client: Request to verify identity.")
                self.info_panel.log_text("Server: Generate nonce and send the challenge to the client.")
                self.info_panel.log_text("Client: Signed challenge by hashing the image data and using sha-256, along with a nonce, to create an HMAC.")
                self.info_panel.log_text("Client: Sending signed challenge to the server across the established communication channel.")
                self.info_panel.log_text("Server: Calculate the expected response and verify against the signed challenge.")
                self.info_panel.log_text("Authentication unsuccessful.\n")
            elif flag == 2:
                self.warning_label.setText("Locked for 10 seconds.")

                self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")
            
            self.warning_label.setVisible(True)
        
        data = self.authentication_service.get_session_stored()
        self.info_panel.update_client_data("Images", ("Images in Bytes", str(images_byte.hex())))
        self.info_panel.update_client_data("Nonce", ("Nonce for Challenge-Response Protocol", byte_str(data["nonce"])))
        self.info_panel.update_client_data("Signed Challenge", ("Signed Challenge", byte_str(data["signed_challenge"])))

        self.info_panel.update_server_data("Nonce", ("Nonce for Challenge-Response Protocol", byte_str(data["nonce"])))
        self.info_panel.update_server_data("Expected Response", ("Expected Response", byte_str(data["expected_response"])))