from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QButtonGroup
from PyQt5.QtGui import QColor
from services.container import ApplicationContainer

# pyright: reportGeneralTypeIssues=false

class QuizButton(QPushButton):
    def __init__(self, parent=None) -> None:
        QPushButton.__init__(self, parent)
        self.setCheckable(True)

        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QuizButton {
                border: 1px solid #6cc8d5;
                background-color: #e2f4f7;
                border-radius: 5%;
                padding: 10px 5px 10px 5px;
                font-size: 11pt;          
            }
            QuizButton:hover {
                background-color: #a7dee6;         
            }
            QuizButton:checked {
                border: 1px solid #048c77;
                background-color: #049c84;         
            }
        """)


class QuizViewModel(QStackedWidget):
    def __init__(self) -> None:
        QStackedWidget.__init__(self)
        self.message_service = ApplicationContainer.message_service()

        self.quiz_settings_page = QuizSettingsViewModel()
        self.quiz_play_page = QuizPlayViewModel()
        self.quiz_response_page = QuizResponseViewModel()
        self.addWidget(self.quiz_settings_page)
        self.addWidget(self.quiz_play_page)
        self.addWidget(self.quiz_response_page)

        self.message_service.subscribe(self, QuizSettingsViewModel, self.on_message)
        self.message_service.subscribe(self, QuizPlayViewModel, self.on_message)
        self.message_service.subscribe(self, QuizResponseViewModel, self.on_message)
    
    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Play Quiz":
            self.quiz_play_page.init_quiz()
            self.setCurrentWidget(self.quiz_play_page)
        elif message_title == "Quiz Response":
            self.quiz_response_page.setup()
            self.setCurrentWidget(self.quiz_response_page)
        elif message_title == "Quiz Settings":
            self.setCurrentWidget(self.quiz_settings_page)


class QuizSettingsViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_settings_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.start_btn.clicked.connect(self.start_quiz)

    def start_quiz(self) -> None:
        self.quiz_service.generate_quiz()
        self.message_service.send(self, "Play Quiz", None)


class QuizPlayViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.saved_choice = ""

        self.button_group = QButtonGroup()

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        shadow_effect.setBlurRadius(50)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        self.frame.setGraphicsEffect(shadow_effect)

        self.next_btn.clicked.connect(self.next_quiz)

    def save_choice(self, choice) -> None:
        self.saved_choice = choice

    def init_quiz(self) -> None:
        quiz = self.quiz_service.get_quiz()
        if quiz:
            self.question_label.setText(str(quiz[0])+". "+quiz[1]["question"])
            
            for i in reversed(range(self.choices_layout.count())):
                    self.choices_layout.itemAt(i).widget().deleteLater()
            for button in self.button_group.buttons():
                self.button_group.removeButton(button)

            for choice in quiz[1]["choices"]:
                choice_button = QuizButton(choice)
                choice_button.clicked.connect(lambda checked, c=choice: self.save_choice(c))
                self.button_group.addButton(choice_button)
                self.choices_layout.addWidget(choice_button)

            self.progress_label.setText(f"<b>{str(quiz[0])}</b> of <b>{str(self.quiz_service.get_quizzes_size())}</b> Questions")
        else:
             self.message_service.send(self, "Quiz Response", None)

    def next_quiz(self) -> None:
        self.quiz_service.sumbit_answer(self.saved_choice)
        self.init_quiz()
    


class QuizResponseViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_response_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.back_btn.clicked.connect(self.back)

    def setup(self) -> None:
        self.difficulty_float.setText(str(self.quiz_service.check_difficulty()))
        result = self.quiz_service.check_answers()
        self.score_int.setText(str(result[0]) + " / " + str(result[1]))
        self.time_val.setText(self.quiz_service.check_time())

    def back(self) -> None:
        self.message_service.send(self, "Quiz Settings", None)