from PyQt5.QtWidgets import QWidget, QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QHBoxLayout, QToolButton
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt
from configuration.app_configuration import Settings


# pyright: reportAttributeAccessIssue=false

class LockableNumberButton(QPushButton):
    def __init__(self, parent: QWidget, text: str, default_color: QColor, pressed_color: QColor, locked: bool) -> None:
        QPushButton.__init__(self, parent, text=text)
        self.default_color = default_color
        self.pressed_color = pressed_color
        self.locked = locked
       
        self.setMinimumSize(100, 53)
        self.setBaseSize(200, 106)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True) 

        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setFixedSize(28, 28)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.setContentsMargins(25, 0, 0, 0)
        self.setLayout(layout)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        shadow_effect.setBlurRadius(40)
        shadow_effect.setXOffset(2)
        self.setGraphicsEffect(shadow_effect)

        self.lock(locked)
    
    def isLocked(self) -> bool:
        return self.locked

    def lock(self, value: bool) -> None:
        if value:
            self.setStyleSheet(
                f"""
                LockableNumberButton {{
                    border-radius: 4px;
                    padding: 12px 12px 12px 75px;
                    background-color: #cccccc;
                    font-size: 12pt;
                    font-weight: bold;
                    text-align: left;
                }}
                """
            )
            self.label.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}lock.svg"))
        else:
            self.setStyleSheet(
                f"""
                LockableNumberButton {{
                    border-radius: 4px;
                    padding: 12px 12px 12px 75px;
                    background-color: {self.default_color.name()};
                    font-size: 12pt;
                    font-weight: bold;
                    text-align: left;
                }}
                LockableNumberButton:checked {{
                    background-color: {self.pressed_color.name()};
                    color: #ffffff;
                }}
                """
            )
            self.label.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}plus-square"))
            self.setChecked(False)
        self.locked = value
    
    def update_icon(self, value: int) -> None:
        if not self.locked:
            if value > 0:
                self.setChecked(True)
                self.label.clear()
                self.label.setText(str(value))
                self.label.setStyleSheet("color: white; border: 2px solid white; border-radius: 5px; font-size: 12pt; font-weight: bold;")
            else:
                self.setChecked(False)
                self.label.setText("")
                self.label.setStyleSheet("")
                self.label.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}plus-square.svg"))
