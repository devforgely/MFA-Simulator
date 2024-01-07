from PyQt5 import uic
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QGraphicsDropShadowEffect, QGroupBox, QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from viewmodels.authentication.authentication_base import *
from services.container import ApplicationContainer
from models.utils import normalise_text

# pyright: reportGeneralTypeIssues=false

class SecurityQuestionRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/register_views/security_question_view.ui", self)
        
        self.minmum_question = 2
        self.maximum_question = 5
        
        self.security_questions = ApplicationContainer.data_service().get_security_questions()
        self.unselected_question = self.security_questions[:]
        self.question_form = []

        self.add_question_btn.clicked.connect(self.add_question)
        self.remove_btn.clicked.connect(self.remove_question)
        self.submit_btn.clicked.connect(self.send)

        # default minimum security questions
        for _ in range(self.minmum_question):
            self.add_question(True)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(50)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        self.setGraphicsEffect(shadow_effect)

    def add_question(self, required: bool) -> None:
        if len(self.question_form) < self.maximum_question:
            layout = self.question_view.layout()
            index = len(self.question_form)

            combo_box = QComboBox()
            combo_box.addItems(self.unselected_question)
            combo_box.currentIndexChanged.connect(self.onComboBoxChanged)

            combo_box.setCursor(Qt.PointingHandCursor)
            combo_box.setStyleSheet("""
                QComboBox::down-arrow {
                    image: url(resources/icons/down-arrow.svg);
                    padding: 0px 24px 10px 0px;
                }
            """)

            answer_lineedit = QLineEdit()

            group_question = QGroupBox(f"Question {index+1} *") if required else QGroupBox(f"Question {index+1}")
            group_answer = QGroupBox("Answer *") if required else QGroupBox("Answer")

            group_question.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
            group_answer.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
            group_question.setLayout(QVBoxLayout())
            group_answer.setLayout(QVBoxLayout())

            group_question.layout().addWidget(combo_box)
            group_answer.layout().addWidget(answer_lineedit)

            group_question.layout().setContentsMargins(1, 1, 1, 1)
            group_answer.layout().setContentsMargins(1, 1, 1, 1)


            layout.addWidget(group_question)
            layout.addWidget(group_answer)
            self.question_form.append((combo_box, answer_lineedit))
            self.onComboBoxChanged()

    def remove_question(self) -> None:
        if len(self.question_form) > self.minmum_question:
            for _ in range(2):
                item = self.question_view.layout().takeAt(self.question_view.layout().count() - 1)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.question_form.pop()

    def onComboBoxChanged(self) -> None:
        self.unselected_question = self.security_questions[:] # copy this array

        for combo_box, _ in self.question_form:
            self.unselected_question.remove(combo_box.currentText())
               
        # update other combo boxes to exclude the selected option
        for combo_box, _ in self.question_form:
            current_text = combo_box.currentText()
            combo_box.blockSignals(True)
            combo_box.clear()

            combo_box.addItem(current_text)
            combo_box.addItems(self.unselected_question)
            combo_box.blockSignals(False)

    def send(self) -> None:
        questions = []
        plain_key = ""
        for question, answer_lineedit in self.question_form:
            if question.currentText() == "-- Select Question --" or len(answer_lineedit.text()) < 3: return
            questions.append(question.currentText())
            plain_key += normalise_text(answer_lineedit.text()) + ";"
        if self.authentication_service.register(plain_key):
            self.authentication_service.session_store({"user_questions":questions})
            self.message_service.send(self, "Registered", None)

class SecurityQuestionAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

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
