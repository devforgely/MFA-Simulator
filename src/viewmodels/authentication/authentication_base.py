from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from services.container import ApplicationContainer

class AuthenticationBaseViewModel(QWidget):
    def __init__(self, ui: str, info_panel: QWidget) -> None:
        QWidget.__init__(self)
        uic.loadUi(ui, self)
        self.authentication_service = ApplicationContainer.authentication_service()
        self.message_service = ApplicationContainer.message_service()
        self.info_panel = info_panel

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(50)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        self.setGraphicsEffect(shadow_effect)

    def initalise_infopanel(self) -> None:
        ...

    def send(self) -> None:
        ...