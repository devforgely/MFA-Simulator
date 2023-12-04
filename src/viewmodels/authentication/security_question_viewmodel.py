from PyQt5 import uic
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit
from viewmodels.authentication.authentication_base import *
from models.utils import normalise_text
import json
import random


class SecurityQuestionRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        try:
            with open('data/security_questions.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("File is not found")
            return
        
        self.minmum_question = 2
        self.maximum_question = 7
        self.selected_questions = []
        self.question_form = []
        
        # Select 9 random questions
        sampled = random.sample(data['securityQuestions'], 9)
        self.selected_questions.append("-- Select Question --")
        self.selected_questions.extend(item['question'] for item in sampled)        

        uic.loadUi("views/register_views/security_question_view.ui", self)

        self.add_question_btn.clicked.connect(self.add_question)
        self.remove_btn.clicked.connect(self.remove_question)
        self.submit_btn.clicked.connect(self.send)

        # default minimum security questions
        for _ in range(self.minmum_question):
            self.add_question()

    def add_question(self) -> None:
        if len(self.question_form) < self.maximum_question:
            layout = self.question_view.layout()
            index = len(self.question_form)

            question_label = QLabel(f"Security Question {index+1}:")
            combo_box = QComboBox()
            combo_box.addItems(self.selected_questions)
            combo_box.currentIndexChanged.connect(self.onComboBoxChanged)
            self.onComboBoxChanged()

            answer_label = QLabel("Your Answer:")
            answer_lineedit = QLineEdit()

            layout.addWidget(question_label, 2*index, 0)
            layout.addWidget(combo_box, 2*index, 1)
            layout.addWidget(answer_label, 2*index+1, 0)
            layout.addWidget(answer_lineedit, 2*index+1, 1)

            self.question_form.append((combo_box, answer_lineedit))

    def remove_question(self) -> None:
        if len(self.question_form) > self.minmum_question:
            for i in range(2):
                for col in range(self.question_view.columnCount()):
                    item = self.question_view.itemAtPosition(2*len(self.question_form) - i - 1, col)
                    if item:
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
                        self.question_view.removeItem(item)
            self.question_form.pop()

    def onComboBoxChanged(self) -> None:
        options = self.selected_questions[:] # copy this array

        for combo_box, _ in self.question_form:
            current_text = combo_box.currentText()
            if current_text != "-- Select Question --":
                options.remove(current_text)
               
        # update other combo boxes to exclude the selected option
        for combo_box, _ in self.question_form:
            current_text = combo_box.currentText()
            combo_box.blockSignals(True)
            combo_box.clear()

            if current_text != "-- Select Question --":
                combo_box.addItem(current_text)
            combo_box.addItems(options)
            combo_box.blockSignals(False)

    def send(self) -> None:
        questions = []
        plain_key = ""
        for question, answer_lineedit in self.question_form:
            questions.append(question.currentText())
            plain_key += normalise_text(answer_lineedit.text()) + ";"
        if self.authentication_service.register(plain_key):
            self.authentication_service.session_store(questions)
            self.plain_key_label.setText(self.authentication_service.get_plain_key())
            self.hashed_key_label.setText(self.authentication_service.get_secret())
            self.timestamp_label.setText(self.authentication_service.get_timestamp())
            self.message_service.send(self, "Registered", None)

class SecurityQuestionAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        self.answer_widgets = []

        uic.loadUi("views/authenticate_views/security_question_view.ui", self)

        self.submit_btn.clicked.connect(self.send)

        self.setup_ui()

    def setup_ui(self) -> None:
        stored = self.authentication_service.get_session_stored()[0] # read-only
        layout = self.question_view.layout()

        # grab the questions for the session storage
        for i in range(len(stored)):
            question_label = QLabel(f"Security Question {i+1}:")
            question_description = QLabel(stored[i])
            answer_label = QLabel("Your Answer:")
            answer_lineedit = QLineEdit()

            layout.addWidget(question_label, 2*i, 0)
            layout.addWidget(question_description, 2*i, 1)
            layout.addWidget(answer_label, 2*i+1, 0)
            layout.addWidget(answer_lineedit, 2*i+1, 1)

            self.answer_widgets.append(answer_lineedit)

    def send(self) -> None:
        plain_key = ""
        for answer_lineedit in self.answer_widgets:
            plain_key += normalise_text(answer_lineedit.text()) + ";"

        truth = self.authentication_service.authenticate(plain_key)
        if truth == True:
            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")
