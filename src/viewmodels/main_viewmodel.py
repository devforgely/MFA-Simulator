from PyQt5 import QtCore, QtGui, QtWidgets, uic


class MainViewModel(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("views/MainView.ui", self)