from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap

# pyright: reportGeneralTypeIssues=false

class ClickableImageLabel(QLabel):
    def __init__(self, image, click_callback, parent=None):
        super().__init__(parent)

        self.image = image
        self.click_callback = click_callback

        # Load the image
        pixmap = QPixmap(image)
        self.setPixmap(pixmap)

        # Set up properties
        self.setAlignment(Qt.AlignCenter) 

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor) 

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor) 

    def mousePressEvent(self, event):
        if self.click_callback:
            self.click_callback(self.image)

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()