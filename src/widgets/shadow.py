from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect, QPushButton
from PyQt5.QtGui import QColor


class ShadowFrame(QFrame):
    def __init__(self, parent=None) -> None:
        QFrame.__init__(self, parent)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setOffset(0, 0)
        shadow_effect.setBlurRadius(50)
        self.setGraphicsEffect(shadow_effect)

    def adjust_shadow(self, opacity, blur_radius, x, y) -> None:
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, opacity))
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setOffset(x, y)
        self.setGraphicsEffect(shadow_effect)

class ShadowButton(QPushButton):
    def __init__(self, parent=None) -> None:
        QPushButton.__init__(self, parent)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setOffset(0, 0)
        shadow_effect.setBlurRadius(50)
        self.setGraphicsEffect(shadow_effect)

    def adjust_shadow(self, opacity, blur_radius, x, y) -> None:
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, opacity))
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setOffset(x, y)
        self.setGraphicsEffect(shadow_effect)