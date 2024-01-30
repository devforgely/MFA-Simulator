from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

class SlidePanel(QWidget):
    def __init__(self, parent=None) -> None:
        QWidget.__init__(self, parent)
        self.is_expanded = True

        self.animation = QPropertyAnimation(self, b'maximumWidth')
        self.animation.setDuration(1000)  # Duration in milliseconds
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)

    def toggle(self):
        if self.maximumWidth() > 0:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(0)
            self.is_expanded = False
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.sizeHint().width())
            self.is_expanded = True

        self.animation.start()