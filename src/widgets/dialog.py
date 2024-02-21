from PyQt5.QtWidgets import QDialog, QPushButton, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation
from PyQt5.QtGui import QMovie
from typing import Callable
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false

class Notification(QDialog):
    def __init__(self, icon, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.duration = 4600

        self.button = QPushButton(icon, "  "+message, self)
        self.button.setFixedSize(280, 35)
        self.button.clicked.connect(self.close_widget)
        self.button.setStyleSheet("background-color: white; border: 1px solid silver; border-radius: 10px")

        effect = QGraphicsOpacityEffect(self.button)
        self.button.setGraphicsEffect(effect)

        self.adjustSize()

        # Create animations for position and opacity
        self.opacity_animation = QPropertyAnimation(effect, b"opacity")

        # Animate opacity
        self.opacity_animation.setDuration(self.duration)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()

        # Auto delete
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_widget)
        self.timer.start(self.duration)
    
    def close_widget(self):
        self.close()

class GifDialog(QDialog):
    def __init__(self, width: int, height: int, func: Callable[[], None], parent=None):
        super(GifDialog, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.trigger = func

        self.overlay = QWidget(self)
        self.overlay.setFixedSize(width, height)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.6);")
        self.adjustSize()

        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setFixedSize(600, 500)
        self.container.setStyleSheet("#container {background-color: white; border-radius: 15%}")
        self.container.move(width // 2 - self.container.width() // 2, height // 2 - self.container.height() // 2)
        
        self.title = QLabel("Congratulations for finishing the simulation!")
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
        self.collect_button.setStyleSheet("background-color: #ffcd27; border-radius: 8%; padding: 7px 15px; font-weight: bold;")
        self.collect_button.clicked.connect(self.close_dialog)
        
        layout = QVBoxLayout(self.container)
        layout.addWidget(self.title)
        layout.addWidget(self.gif_label)
        layout.addWidget(self.collect_button, alignment=Qt.AlignCenter)
        
        # Start the GIF
        self.movie.start()

    def close_dialog(self) -> None:
        self.trigger()
        self.close()