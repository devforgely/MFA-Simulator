from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit
from PyQt5.QtGui import QPixmap
from services.container import ApplicationContainer
import os
import random

class ClickableImageLabel(QLabel):
    def __init__(self, image, click_callback, parent=None):
        super().__init__(parent)

        self.image = image
        self.click_callback = click_callback

        # Load the image
        pixmap = QPixmap(image)
        self.setPixmap(pixmap)

        # Set up properties
        self.setAlignment(Qt.AlignCenter) # type: ignore

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor) # type: ignore

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor) # type: ignore

    def mousePressEvent(self, event):
        if self.click_callback:
            self.click_callback(self.image)

class ImagePasswordRegisterViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.selected_images = []

        # Specify the folder path of images
        self.folder_path = 'data/images/'
        # Load images from the folder
        self.images = [self.folder_path+f for f in os.listdir(self.folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

        uic.loadUi("views/register_views/image_password_view.ui", self)

        self.password_field.setEchoMode(QLineEdit.Password)
        self.refresh_btn.clicked.connect(self.refresh_images)
        self.reset_btn.clicked.connect(lambda: self.selected_images.clear())
        self.submit_btn.clicked.connect(self.send)

        # inital setup for images on grid layout
        self.refresh_images()

    def refresh_images(self) -> None:
        print("refresh image")
        #clear widget on the grid
        while self.image_view.count():
            item = self.image_view.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        layout = self.image_view.layout()

        temp_images = self.images[:] #copy
        # filter over selected images
        temp_images = [x for x in temp_images if x not in self.selected_images]
        random.shuffle(self.images)

        # 3 by 3 grid
        # Add images that is not selected to the grid
        row, col = 0, 0
        for img in temp_images:
            label = ClickableImageLabel(img, self.on_image_click, self)
            layout.addWidget(label, row, col)

            if (row == 2 and col == 2):
                break

            col += 1
            if col > 2:
                col = 0
                row += 1

    def on_image_click(self, image: str) -> None:
        print(image)
        if image in self.selected_images:
            self.selected_images.remove(image)
        else:
            self.selected_images.append(image)
        self.select_lbl.setText(f"Selected Image Count: {len(self.selected_images)}")

    def send(self) -> None:
        print("sending")
        imgs_combined = ""
        self.selected_images.sort()
        for img in self.selected_images:
            imgs_combined += img + ";"

        plain_key = imgs_combined+self.password_field.text()
        self.authentication_service.session_store(self.selected_images)
        hashed_key = self.authentication_service.register(plain_key)
        if hashed_key != "":
            self.message_service.send(self, "Change View", None)



class ImagePasswordAuthenticateViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()

        self.selected_images = []

        # Specify the folder path of images
        self.folder_path = 'data/images/'
        # Load images from the folder
        self.images = [self.folder_path+f for f in os.listdir(self.folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

        uic.loadUi("views/authenticate_views/image_password_view.ui", self)
        
        self.password_field.setEchoMode(QLineEdit.Password)
        self.refresh_btn.clicked.connect(self.refresh_images)
        self.reset_btn.clicked.connect(lambda: self.selected_images.clear())
        self.submit_btn.clicked.connect(self.send)

        # inital setup for images on grid layout
        self.refresh_images()

    def refresh_images(self) -> None:
        print("refresh image")
        #clear widget on the grid
        while self.image_view.count():
            item = self.image_view.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        layout = self.image_view.layout()

        temp_images = self.images[:] #copy

        # get a copy of the selected image and filter over selected images
        stored = self.authentication_service.get_session_stored()[0][:]
        stored = [x for x in stored if x not in self.selected_images]

        # filter over selected images and stored images
        temp_images = [x for x in temp_images if x not in stored]
        temp_images = [x for x in temp_images if x not in self.selected_images]
        random.shuffle(self.images)
        
        # add a random image from stored that is not selected into temp images
        i = random.randint(0, len(stored) - 1)
        j = random.randint(0, 8)
        temp_images.insert(j, stored[i])
        
        # 3 by 3 grid
        # Add images that is not selected to the grid
        row, col = 0, 0
        for img in temp_images:
            label = ClickableImageLabel(img, self.on_image_click, self)
            layout.addWidget(label, row, col)

            if (row == 2 and col == 2):
                break

            col += 1
            if col > 2:
                col = 0
                row += 1

    def on_image_click(self, image: str) -> None:
        print(image)
        if image in self.selected_images:
            self.selected_images.remove(image)
        else:
            self.selected_images.append(image)
        self.select_lbl.setText(f"Selected Image Count: {len(self.selected_images)}")

    def send(self) -> None:
        print("sending")
        imgs_combined = ""
        self.selected_images.sort()
        for img in self.selected_images:
            imgs_combined += img + ";"

        plain_key = imgs_combined+self.password_field.text()
        truth = self.authentication_service.authenticate(plain_key)
        if truth == True:
            self.message_service.send(self, "Change View", None)
        else:
            print("wrong key")