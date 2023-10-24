from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class PlaceHolderViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)

        uic.loadUi("views/placeholder_view.ui", self) 