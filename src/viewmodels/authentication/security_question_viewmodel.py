from PyQt5 import uic
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QGroupBox, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt
from viewmodels.authentication.authentication_base import *
from services.container import ApplicationContainer
from models.utils import normalise_text

# pyright: reportGeneralTypeIssues=false

class CustemComboBox(QComboBox):
    def __init__(self, parent = None):
        super(CustemComboBox,self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, e):
        e.ignore()
        pass

class SecurityQuestionRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/register_views/security_question_view.ui", self)

        self.info_panel.add_client_data("questions", "null")
        self.info_panel.add_client_data("answers", "null")
        
        self.info_panel.add_server_data("user_questions", "null")
        self.info_panel.add_server_data("user_answers", "null")

        self.info_panel.log_text("Waiting for security questions and answers...")
        
        self.minmum_question = 2
        self.maximum_question = 5
        
        self.security_questions = ApplicationContainer.data_service().get_security_questions()
        self.unselected_question = self.security_questions[:]
        self.question_form = []

        self.add_question_btn.clicked.connect(self.add_question)
        self.remove_btn.clicked.connect(self.remove_question)
        self.submit_btn.clicked.connect(self.send)

        self.question_view.layout().addStretch()
        # default minimum security questions
        for _ in range(self.minmum_question):
            self.add_question(True)

    def add_question(self, required: bool) -> None:
        if len(self.question_form) < self.maximum_question:
            layout = self.question_view.layout()
            index = len(self.question_form)

            combo_box = CustemComboBox()
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


            layout.insertWidget(layout.count() - 1, group_question)
            layout.insertWidget(layout.count() - 1, group_answer)
            self.question_form.append((combo_box, answer_lineedit))
            self.onComboBoxChanged()

    def remove_question(self) -> None:
        if len(self.question_form) > self.minmum_question:
            for _ in range(2):
                item = self.question_view.layout().takeAt(self.question_view.layout().count() - 2)
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
            if len(answer_lineedit.text()) < 3: return
            questions.append(question.currentText())
            plain_key += normalise_text(answer_lineedit.text()) + ";"
        if self.authentication_service.register(plain_key):
            self.authentication_service.session_store({"user_questions":questions})

            self.info_panel.update_client_status("request", "registration")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_register"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user registered")

            self.info_panel.update_client_data("questions", str(questions))
            self.info_panel.update_client_data("answers", plain_key)

            self.info_panel.update_server_data("user_questions", str(self.authentication_service.get_session_stored()["user_questions"]))
            self.info_panel.update_server_data("user_answers", self.authentication_service.get_session_stored()["key"])

            self.info_panel.log_text(f"Client: {len(questions)} security question selected and all answers entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Registering user with security questions and answers.")
            self.info_panel.log_text("Registeration successful.")

            self.message_service.send(self, "Registered", None)


class SecurityQuestionAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__(info_panel)

        uic.loadUi("views/authenticate_views/security_question_view.ui", self)

        self.info_panel.add_client_data("questions", str(self.authentication_service.get_session_stored()["user_questions"]))
        self.info_panel.add_client_data("answers", "null")
        
        self.info_panel.add_server_data("user_questions", str(self.authentication_service.get_session_stored()["user_questions"]))
        self.info_panel.add_server_data("user_answers", self.authentication_service.get_session_stored()["key"])

        self.info_panel.log_text("Waiting for answers to security questions...")
        
        self.answer_widgets = []

        self.submit_btn.clicked.connect(self.send)
        self.setup_ui()

    def setup_ui(self) -> None:
        stored = self.authentication_service.get_session_stored()["user_questions"]
        layout = self.question_view.layout()

        # grab the questions for the session storage
        for index in range(len(stored)):
            question_label = QLabel(stored[index])
            answer_lineedit = QLineEdit()

            group_question = QGroupBox(f"Question {index+1} *")
            group_answer = QGroupBox("Answer *")

            group_question.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
            group_answer.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
            group_question.setLayout(QVBoxLayout())
            group_answer.setLayout(QVBoxLayout())

            group_question.layout().addWidget(question_label)
            group_answer.layout().addWidget(answer_lineedit)

            group_question.layout().setContentsMargins(1, 1, 1, 4)
            group_answer.layout().setContentsMargins(1, 1, 1, 1)

            layout.addWidget(group_question)
            layout.addWidget(group_answer)

            self.answer_widgets.append(answer_lineedit)
        layout.addStretch()

    def send(self) -> None:
        plain_key = ""
        for answer_lineedit in self.answer_widgets:
            plain_key += normalise_text(answer_lineedit.text()) + ";"

        if self.authentication_service.authenticate(plain_key):
            self.info_panel.update_client_status("request", "authentication")
            self.info_panel.update_client_status("timestamp", self.authentication_service.get_session_stored()["timestamp_authenticate"])

            self.info_panel.update_server_status("status", "200")
            self.info_panel.update_server_status("message", "user authenticated")

            self.info_panel.update_client_data("answers", plain_key)

            self.info_panel.log_text(f"Client: {len(self.answer_widgets)} security question displayed and all answers entered.")
            self.info_panel.log_text("Client: Sending data through HTTPS protocol.")
            self.info_panel.log_text("Server: Verifying user against answers.")
            self.info_panel.log_text("Authentication successful.")

            self.message_service.send(self, "Authenticated", None)
        else:
            print("wrong key")
