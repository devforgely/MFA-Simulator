from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QLineEdit, QToolButton, QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QIcon
from configuration.app_settings import Settings

# pyright: reportAttributeAccessIssue=false

class BorderedImageLabel(QLabel):
    clicked = pyqtSignal(QLabel)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = ""
    
    def set_image(self, image) -> None:
        self.image = image
    
    def mousePressEvent(self, event):
        self.clicked.emit(self)
    
    def show_border(self) -> None:
        self.setStyleSheet('border: 3px solid blue;')
    
    def hide_border(self) -> None:
        self.setStyleSheet('border: none;')


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()

class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder: str, visibility: bool, maxlength: int, icon: str):
        super(CustomLineEdit, self).__init__()

        self.setFrame(False)
        self.setStyleSheet("""
            QLineEdit {
                height: 52px;
                margin: 7px 0;
                padding: 0px 15px;
                padding-left: 35px;
                border-bottom: 2px solid #bbbdbf;
                font-size: 10pt;
                font-weight: 400;
                color: #333;
            }

            QLineEdit:focus {
                border-color: #4070f4;
            }
        """)

        self.setPlaceholderText(placeholder)
        self.setMaxLength(maxlength)
        # Create a layout for the QLineEdit
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)
        self.icon = QLabel(self)
        self.icon.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}{icon}.svg"))
        layout.addWidget(self.icon)
        # Add a stretchable space in the middle
        layout.addStretch()

        if not visibility:        
            self.setEchoMode(QLineEdit.Password)
            self.eye_button = QToolButton(self)
            self.eye_button.setCursor(Qt.PointingHandCursor)
            self.eye_button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}eye.svg"))

            self.eye_button.setStyleSheet("""
                QToolButton {
                    border: none;
                    alignment: 5px 0px 5px 200px;
                }
            """)

            # Add the eye button to the right
            layout.addWidget(self.eye_button)
            self.eye_button.clicked.connect(self.toggle_password_visibility)

    def toggle_password_visibility(self):
        if self.echoMode() == QLineEdit.Password:
            self.eye_button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}eye-off.svg"))
            self.setEchoMode(QLineEdit.Normal)
        else:
            self.eye_button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}eye.svg"))
            self.setEchoMode(QLineEdit.Password)