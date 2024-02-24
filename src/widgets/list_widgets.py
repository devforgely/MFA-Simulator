from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon
from configuration.app_configuration import Settings

class ToggleListItem(QWidget):
    def __init__(self, title: str, text: str, mode: bool, parent=None):
        super(ToggleListItem, self).__init__(parent)
        layout = QVBoxLayout(self)

        self.button = QPushButton(title)
        size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.button.setSizePolicy(size_policy)
        
        if mode:
            self.button.setIcon(QIcon(Settings.ICON_FILE_PATH+"check.svg"))
        else:
            self.button.setIcon(QIcon(Settings.ICON_FILE_PATH+"x.svg"))

        self.text = QLabel()
        self.text.setWordWrap(True)
        self.text.setText(text)
        self.text.hide()

        layout.addWidget(self.button)
        layout.addWidget(self.text)

        self.button.clicked.connect(self.toggle_text)

    def toggle_text(self):
        if self.text.isVisible():
            self.text.hide()
        else:
            self.text.show()