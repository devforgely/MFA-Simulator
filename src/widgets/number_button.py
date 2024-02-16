from PyQt5.QtWidgets import QWidget, QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QHBoxLayout
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt
from configuration.app_settings import Settings


# pyright: reportAttributeAccessIssue=false

class NumberButton(QPushButton):
    def __init__(self, parent: QWidget, text: str, default_color: QColor, pressed_color: QColor) -> None:
        QPushButton.__init__(self, parent, text=text)
        self.default_color = default_color
        self.pressed_color = pressed_color

        self.setStyleSheet(
            f"""
            NumberButton {{
                border-radius: 4px;
                padding: 12px 12px 12px 75px;
                background-color: {self.default_color.name()};
                font-size: 12pt;
                font-weight: bold;
                text-align: left;
            }}
            NumberButton:checked {{
                background-color: {self.pressed_color.name()};
                color: #ffffff;
            }}
            """
        )
        self.setMinimumSize(100, 53)
        self.setBaseSize(200, 106)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True) 

        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setFixedSize(28, 28)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: none;")
        self.label.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}plus-square"))

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.setContentsMargins(25, 0, 0, 0)
        self.setLayout(layout)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(40)
        shadow_effect.setXOffset(2)
        self.setGraphicsEffect(shadow_effect)
    
    def update_icon(self, value: int) -> None:
        if value > 0 and value < 8:
            self.label.clear()
            self.label.setText(str(value))
            self.label.setStyleSheet("color: white; border: 2px solid white; border-radius: 5px; font-size: 12pt; font-weight: bold;")
        else:
            self.label.setText("")
            self.label.setStyleSheet("border: none;")
            self.label.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}plus-square"))