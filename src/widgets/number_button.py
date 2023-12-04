from PyQt5.QtWidgets import QWidget, QPushButton, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt

# pyright: reportGeneralTypeIssues=false

class NumberButton(QPushButton):
    def __init__(self, parent: QWidget, text: str, default_color: QColor, pressed_color: QColor) -> None:
        QPushButton.__init__(self, parent, text=text)
        self.default_color = default_color
        self.pressed_color = pressed_color

        self.setStyleSheet(
            f"""
            QPushButton {{
                border-radius: 4px;
                padding: 12px;
                background-color: {self.default_color.name()};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {self.pressed_color.name()};
                color: #ffffff;
            }}
            """
        )
        self.setMinimumSize(100, 53)
        self.setBaseSize(200, 106)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(u"resources/icons/add-circle.svg"))
        self.setCheckable(True)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(40)
        shadow_effect.setXOffset(2)
        self.setGraphicsEffect(shadow_effect)