from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from configuration.app_configuration import Settings
from PyQt5 import uic

# pyright: reportAttributeAccessIssue=false

class GifDialog(QDialog):
    def __init__(self, parent=None):
        super(GifDialog, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        if parent:
            self.resize(parent.size())
            parent.resized.connect(self.parent_resized)

        self.setObjectName("form")
        self.setStyleSheet("#form {background-color: rgba(0, 0, 0, 0.6)}")

        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setFixedSize(600, 500)
        self.container.setStyleSheet("#container {background-color: white; border-radius: 15%}")
        self.container.move(self.width() // 2 - self.container.width() // 2, self.height() // 2 - self.container.height() // 2)
        
        self.title = QLabel("Congratulations on finishing the simulation!")
        self.title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.title.setAlignment(Qt.AlignCenter)

        # Create a QLabel to hold the GIF
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie(Settings.IMAGE_FILE_PATH+"confetti.gif")
        self.gif_label.setMovie(self.movie)

        self.collect_button = QPushButton("Collect")
        self.collect_button.setMinimumWidth(200)
        self.collect_button.setCursor(Qt.PointingHandCursor)
        self.collect_button.setStyleSheet("""
                                          QPushButton { background-color: #ffcd27; border-radius: 8%; padding: 7px 15px; font-weight: bold; }
                                          QPushButton:hover { background-color: #e6b923; }
                                          """)
        self.collect_button.clicked.connect(self.close_dialog)
        
        layout = QVBoxLayout(self.container)
        layout.addWidget(self.title)
        layout.addWidget(self.gif_label)
        layout.addWidget(self.collect_button, alignment=Qt.AlignCenter)
        
        # Start the GIF
        self.movie.start()

    def close_dialog(self) -> None:
        self.close()

    def parent_resized(self):
        self.resize(self.parent().size())

    def resizeEvent(self, event):
        self.container.move(self.width() // 2 - self.container.width() // 2, self.height() // 2 - self.container.height() // 2)
        super(GifDialog, self).resizeEvent(event)

class DetailViewDialog(QDialog):
    def __init__(self, title: str, details: str, parent=None):
        super(DetailViewDialog, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        if parent:
            parent.resized.connect(self.parent_resized)

        self.setObjectName("form")
        self.setStyleSheet("#form {background-color: rgba(0, 0, 0, 0.6)}")
        if parent is not None:
            self.resize(parent.size())

        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setFixedSize(600, 500)
        self.container.setStyleSheet("#container {background-color: white; border-radius: 15%; padding: 20px 30px;}")
        self.container.move(self.width() // 2 - self.container.width() // 2, self.height() // 2 - self.container.height() // 2)
        
        self.header = QWidget(self)
        self.header.setStyleSheet("font-weight: bold; font-size: 12pt; border-bottom: 2px solid #1b232f;")
        layout = QVBoxLayout(self.header)
        self.title = QLabel(title)
        layout.addWidget(self.title)

        # Create a QLabel to hold the details
        self.detail_label = QTextEdit()
        self.detail_label.setReadOnly(True)
        self.detail_label.setStyleSheet("QTextEdit { border: 1px solid gray; padding: 10px; } QTextEdit::-webkit-scrollbar { width: 0px; }")
        self.detail_label.setPlainText(details)

        self.close_button = QPushButton("Close")
        self.close_button.setMinimumWidth(200)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("""
                                        QPushButton { background-color: #545aea; color: #fff; border-radius: 15%; padding: 7px 15px; font-weight: bold; }
                                        QPushButton:hover { background-color: #4c51d3; }
                                        """)
        self.close_button.clicked.connect(self.close_dialog)
        
        layout = QVBoxLayout(self.container)
        layout.addWidget(self.header)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter | Qt.AlignBottom)

    def close_dialog(self) -> None:
        self.close()

    def parent_resized(self):
        self.resize(self.parent().size())

    def resizeEvent(self, event):
        self.container.move(self.width() // 2 - self.container.width() // 2, self.height() // 2 - self.container.height() // 2)
        super(DetailViewDialog, self).resizeEvent(event)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

        uic.loadUi("views_ui/about_view.ui", self)

        if parent is not None:
            self.resize(parent.size())

        self.exit_about.clicked.connect(self.close_dialog)

    def close_dialog(self) -> None:
        self.close()
        
