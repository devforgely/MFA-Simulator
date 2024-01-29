from PyQt5.QtWidgets import QLineEdit
from viewmodels.authentication.authentication_base import *
from widgets.clickables import ClickableImageLabel
import os
import random


class ImagePasswordRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget, ui="views/register_views/image_password_view.ui") -> None:
        super().__init__(ui, info_panel)

        self.MAX_SELECT_COUNT = 7

        self.selected_images = []

        # Specify the folder path of images
        self.folder_path = 'data/images/'
        # Load images from the folder
        self.images = [self.folder_path+f for f in os.listdir(self.folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

        self.visible_check.clicked.connect(self.toggle_border_visibility)
        self.password_field.setEchoMode(QLineEdit.Password)
        self.refresh_btn.clicked.connect(self.refresh_images)
        self.reset_btn.clicked.connect(self.reset)
        self.submit_btn.clicked.connect(self.send)

        # inital setup for images on grid layout
        self.refresh_images()

        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("images", [])
        self.info_panel.add_client_data("password", "null")
        
        self.info_panel.add_server_data("user_images", [])
        self.info_panel.add_server_data("user_password", "null")

        self.info_panel.log_text("Waiting for images and password...")
    
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
        layout = self.image_view.layout()
        #clear widget on the grid
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        temp_images = self.images[:] #copy
        # filter over selected images
        temp_images = [x for x in temp_images if x not in self.selected_images]
        random.shuffle(self.images)

        # 3 by 3 grid
        # Add images that is not selected to the grid
        row, col = 0, 0
        for img in temp_images:
            label = ClickableImageLabel(img, self.on_image_click)
            layout.addWidget(label, row, col)

            if (row == 2 and col == 2):
                break

            col += 1
            if col > 2:
                col = 0
                row += 1

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
        self.password_field.clear()

        layout = self.image_view.layout()
        for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.hide_border()

    def send(self) -> None:
        imgs_combined = ""
        self.selected_images.sort()
        for img in self.selected_images:
            imgs_combined += img + ";"

        plain_key = imgs_combined+self.password_field.text()
        if self.authentication_service.register(plain_key):
            self.authentication_service.session_store({"user_images":self.selected_images})

            self.info_panel.update_client_status("request", "registration")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user registered")

            self.info_panel.update_client_data("images", self.selected_images)
            self.info_panel.update_client_data("password", plain_key)

            self.info_panel.update_server_data("user_images", self.authentication_service.get_session_stored()["user_images"])
            self.info_panel.update_server_data("user_password", self.authentication_service.get_session_stored()["key"])

            self.info_panel.log_text(f"Client: {len(self.selected_images)} images selected and password entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Registering user with images and password.")
            self.info_panel.log_text("Registeration successful.")

            self.message_service.send(self, "Registered", None)



class ImagePasswordAuthenticateViewModel(ImagePasswordRegisterViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel, ui="views/authenticate_views/image_password_view.ui")

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("images", [])
        self.info_panel.add_client_data("password", "null")
        
        self.info_panel.add_server_data("user_images", self.authentication_service.get_session_stored()["user_images"])
        self.info_panel.add_server_data("user_password", self.authentication_service.get_session_stored()["key"])

        self.info_panel.log_text("Waiting for images and password...")

    def send(self) -> None:
        imgs_combined = ""
        self.selected_images.sort()
        for img in self.selected_images:
            imgs_combined += img + ";"

        plain_key = imgs_combined+self.password_field.text()
        if self.authentication_service.authenticate(plain_key):
            self.info_panel.update_client_status("request", "authentication")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_authenticate"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user authenticated")

            self.info_panel.update_client_data("images", self.selected_images)
            self.info_panel.update_client_data("password", plain_key)

            self.info_panel.log_text(f"Client: {len(self.selected_images)} images selected and password entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Verifying user against database.")
            self.info_panel.log_text("Authentication successful.")

            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")