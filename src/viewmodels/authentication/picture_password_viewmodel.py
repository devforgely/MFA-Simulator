from viewmodels.authentication.authentication_base import *
from PyQt5.QtWidgets import QWidget
import os
import random
from models.utils import encrypt_images, byte_str
from configuration.app_configuration import Settings


class PicturePasswordRegisterViewModel(AuthenticationBaseViewModel):
    security_measure_changed = pyqtSignal(int)
    refresh_images_signal = pyqtSignal(list)
    select_count_change = pyqtSignal(str)
    select_signal = pyqtSignal(QWidget, bool)
    reset_selection_signal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()

        self.MAX_SELECT_COUNT = 7

        self.selected_images = []
        self.viewed_images = []

        # Load images from the folder
        self.images = [Settings.PICTURE_FILE_PATH+f for f in os.listdir(Settings.PICTURE_FILE_PATH) if f.endswith(('.png', '.jpg', '.jpeg'))]

    def refresh_images(self) -> None:
        random.shuffle(self.images)
        # filter over selected images
        temp_images = [x for x in self.images if x not in self.selected_images and x not in self.viewed_images][:9] #copy

        if len(temp_images) < 9:
            random.shuffle(self.viewed_images)
            temp_images.extend(random.sample(self.viewed_images, 9-len(temp_images)))
            self.viewed_images.clear()

        self.viewed_images.extend(temp_images)
        self.refresh_images_signal.emit(temp_images)

    def on_image_click(self, widget: QWidget) -> None:
        if widget.image in self.selected_images:
            self.remove_selection(widget.image)
            self.select_signal.emit(widget, False)
        elif len(self.selected_images) < self.MAX_SELECT_COUNT:
            self.add_selection(widget.image)
            self.select_signal.emit(widget, True)

    def remove_selection(self, image: str) -> None:
        self.selected_images.remove(image)
        self.select_count_change.emit(f"Selected Image Count: {len(self.selected_images)}")
        self.security_measure_changed.emit(len(self.selected_images)*10)

    def add_selection(self, image: str) -> None:
        self.selected_images.append(image)
        self.select_count_change.emit(f"Selected Image Count: {len(self.selected_images)}")
        self.security_measure_changed.emit(len(self.selected_images)*10)

    def reset_selection(self) -> None:
        self.selected_images.clear()
        self.select_count_change.emit("Selected Image Count: 0")
        self.security_measure_changed.emit(0)
        self.reset_selection_signal.emit()

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["user_images"] = byte_str(data["user_images"])
        data["hashed_secret"] = byte_str(data["hashed_secret"])
        data["encryption_key"] = byte_str(data["encryption_key"])
        data["iv"] = byte_str(data["iv"])
        return data

    def send(self) -> None:
        if len(self.selected_images) == 0:
            self.state_change.emit("Please select some images to proceed Registration.", 1)
        else:
            key = os.urandom(32)
            iv = os.urandom(32)
            images_byte = encrypt_images(self.selected_images, key, iv)

            if self.authentication_service.register(images_byte):
                self.authentication_service.session_store({"encryption_key": key, "iv": iv})
                self.state_change.emit("Account has been registered.", 0)
                self.state_data_change.emit(self.state_data(), 0)
                self.message_service.send(self, "Registered")
            else:
                self.state_change.emit("Registration Fail", 1)


class PicturePasswordAuthenticateViewModel(PicturePasswordRegisterViewModel):
    def __init__(self) -> None:
        super().__init__()

    def remove_selection(self, image: str) -> None:
        self.selected_images.remove(image)
        self.select_count_change.emit(f"Selected Image Count: {len(self.selected_images)}")

    def add_selection(self, image: str) -> None:
        self.selected_images.append(image)
        self.select_count_change.emit(f"Selected Image Count: {len(self.selected_images)}")

    def reset_selection(self) -> None:
        self.selected_images.clear()
        self.select_count_change.emit("Selected Image Count: 0")
        self.reset_selection_signal.emit()
    
    def state_data(self, is_checked: bool) -> dict:
        data = self.authentication_service.get_session_stored().copy()

        data["hashed_secret"] = byte_str(data["hashed_secret"])
        if is_checked:
            data["images"] = byte_str(data["images"])
            data["nonce"] = byte_str(data["nonce"])
            data["signed_challenge"] = byte_str(data["signed_challenge"])
            data["expected_response"] = byte_str(data["expected_response"])

        return data

    def send(self) -> None:
        data = self.authentication_service.get_session_stored()
        encryption_key = data["encryption_key"]
        iv = data["iv"]
        images_byte = encrypt_images(self.selected_images, encryption_key, iv)

        flag = self.authentication_service.authenticate(images_byte)
        if not flag:
            self.state_change.emit("The user has been authenticated.", 0)
            self.message_service.send(self, "Authenticated")
        elif flag == 1:
            self.state_change.emit("These credentials does not match our records.", flag)
        elif flag == 2:
            self.state_change.emit("Locked for 10 seconds.", flag)

        self.state_data_change.emit(self.state_data(True), flag)
    
    def bypass(self) -> None:
        self.state_data_change.emit(self.state_data(True), 0)
    
