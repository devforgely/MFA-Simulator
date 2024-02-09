from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor


class ShadowFrame(QFrame):
    def __init__(self, parent=None) -> None:
        QFrame.__init__(self, parent)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(50)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        self.setGraphicsEffect(shadow_effect)