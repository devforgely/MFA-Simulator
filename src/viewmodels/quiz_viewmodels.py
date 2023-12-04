from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget
from services.container import ApplicationContainer


class QuizViewModel(QStackedWidget):
    def __init__(self) -> None:
        QStackedWidget.__init__(self)
        self.message_service = ApplicationContainer.message_service()

        self.quiz_settings_page = QuizSettingsViewModel()
        self.quiz_play_page = QuizPlayViewModel()
        self.addWidget(self.quiz_settings_page)
        self.addWidget(self.quiz_play_page)

        self.message_service.subscribe(self, QuizSettingsViewModel, self.on_message)
        self.message_service.subscribe(self, QuizPlayViewModel, self.on_message)
    
    def on_message(self, message_title: str, *args: Any) -> None:
        ...


class QuizSettingsViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_settings_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()


class QuizPlayViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()