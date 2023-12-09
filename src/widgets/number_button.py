from PyQt5.QtWidgets import QWidget, QPushButton, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt

# pyright: reportGeneralTypeIssues=false

class NumberButton(QPushButton):
    def __init__(self, parent: QWidget, text: str, default_color: QColor, pressed_color: QColor) -> None:
        QPushButton.__init__(self, parent, text=text)
        self.default_color = default_color
        self.pressed_color = pressed_color

        self.setStyleSheet(
            f"""
            NumberButton {{
                border-radius: 4px;
                padding: 12px;
                background-color: {self.default_color.name()};
                font-size: 12pt;
                font-weight: bold;
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
        self.setIcon(QIcon(u"resources/icons/plus-square.svg"))
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(40)
        shadow_effect.setXOffset(2)
        self.setGraphicsEffect(shadow_effect)
    
    def update_icon(self, value: int) -> None:
        match value:
            case 1:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case 2:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case 3:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case 4:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case 5:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case 6:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case 7:
                self.setIcon(QIcon(u"resources/icons/plus-square-white.svg"))
            case _:
                self.setIcon(QIcon(u"resources/icons/plus-square.svg"))