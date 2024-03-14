from PyQt5.QtWidgets import QMainWindow, QButtonGroup
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from configuration.app_configuration import Settings


# pyright: reportAttributeAccessIssue=false

class HelpView(QMainWindow):
    def __init__(self, viewmodel, ui="views_ui/help_view.ui") -> None:
        super().__init__()
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self._viewmodel.search_changed.connect(self.stackedWidget.setCurrentIndex)

        self.setWindowTitle("MFA Simulator Helper")
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.quick_start_btn)
        self.button_group.addButton(self.simulate_btn)
        self.button_group.addButton(self.learn_btn)
        self.button_group.addButton(self.quiz_btn)
        self.button_group.addButton(self.profile_btn)
        self.button_group.addButton(self.manage_btn)

        self.quick_start_btn.clicked.connect(self.button_click)
        self.simulate_btn.clicked.connect(self.button_click)
        self.learn_btn.clicked.connect(self.button_click)
        self.quiz_btn.clicked.connect(self.button_click)
        self.profile_btn.clicked.connect(self.button_click)
        self.manage_btn.clicked.connect(self.button_click)

        self.quick_start_btn.setChecked(True)
        self.stackedWidget.setCurrentIndex(0)

        self.search_field.returnPressed.connect(self.search_text)

        self.current_theme = "dark"
        self.theme_btn.clicked.connect(self.change_theme)
        self.change_theme()
        self.show()

    def search_text(self):
        self._viewmodel.search(self.search_field.text())

    def button_click(self):
        btn_name = self.sender().objectName()

        match(btn_name):
            case "quick_start_btn":
                self.stackedWidget.setCurrentIndex(0)
            case "simulate_btn":
                self.stackedWidget.setCurrentIndex(1)
            case "learn_btn":
                self.stackedWidget.setCurrentIndex(2)
            case "quiz_btn":
                self.stackedWidget.setCurrentIndex(3)
            case "profile_btn":
                self.stackedWidget.setCurrentIndex(4)
            case "manage_btn":
                self.stackedWidget.setCurrentIndex(5)
            case _:
                Exception("Undefined Button Behaviour")

    def change_theme(self) -> None:
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.theme_btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"moon.svg"))
            self.search_icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH+"search-dark.svg"))
            self.menu.setStyleSheet("#menu { background-color: #1a1c1e; border-right: 1px solid silver; }")
            self.title.setStyleSheet("font-size: 14pt; margin: 20px 0px; margin-right: 10px; color: #dedede;")
            self.container.setStyleSheet("#container { background-color: #131416; } QLabel {color: #dedede; font-size: 10pt;}")
        else:
            self.current_theme = "light"
            self.theme_btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"sun.svg"))
            self.search_icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH+"search-light.svg"))
            self.menu.setStyleSheet("#menu { background-color: #f8f9fb; border-right: 1px solid silver; }")
            self.title.setStyleSheet("font-size: 14pt; margin: 20px 0px; margin-right: 10px; color: #000; ")
            self.container.setStyleSheet("#container { background-color: #fff; } QLabel {color: #000; font-size: 10pt;}")