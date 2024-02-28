from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QGroupBox, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt
from viewmodels.authentication.authentication_base import *
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from models.utils import normalise_text, parse_array, byte_str
from widgets.info_panel import InfoMode

# pyright: reportAttributeAccessIssue=false

class CustemComboBox(QComboBox):
    def __init__(self, parent = None):
        super(CustemComboBox,self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, e):
        e.ignore()
        pass

class SecurityQuestionRegisterViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/register_views/security_question_view.ui", info_panel)

        self.MINIMUM_QUESTION = 2
        self.MAXIMUM_QUESTION = 5
        
        self.security_questions = ApplicationContainer.data_service().get_security_questions()
        self.unselected_question = self.security_questions[:]
        self.question_form = []

        self.add_question_btn.clicked.connect(self.add_question)
        self.remove_btn.clicked.connect(self.remove_question)
        self.submit_btn.clicked.connect(self.send)

        self.question_view.layout().addStretch()
        # default minimum security questions
        for _ in range(self.MINIMUM_QUESTION):
            self.add_question(True)

        self.initalise_infopanel()

        self.frame.adjust_shadow(30, 50, 2, 2)

    def initalise_infopanel(self) -> None:
        self.info_panel.add_client_data("Security Questions", ("Security Questions", "[]"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Answers", ("Answers", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Security Questions", ("User Security Questions", "[]"), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Security Answers", ("User Security Answers", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Server: Generate a set of security questions and send to client.")
        self.info_panel.log_text("Waiting for security questions and answers...\n")
        self.info_panel.set_measure_level(40)

    def add_question(self, required: bool) -> None:
        if len(self.question_form) < self.MAXIMUM_QUESTION:
            layout = self.question_view.layout()
            index = len(self.question_form)

            combo_box = CustemComboBox()
            combo_box.addItems(self.unselected_question)
            combo_box.currentIndexChanged.connect(self.onComboBoxChanged)

            combo_box.setCursor(Qt.PointingHandCursor)
            combo_box.setStyleSheet(f"""
                QComboBox::down-arrow {{
                    image: url({Settings.ICON_FILE_PATH}down-arrow.svg);
                    padding: 0px 24px 10px 0px;
                }}
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
        if len(self.question_form) > self.MINIMUM_QUESTION:
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
            if len(answer_lineedit.text()) < 3:
                self.warning_label.setStyleSheet("color: #d5786c;")
                return
            questions.append(question.currentText())
            plain_key += normalise_text(answer_lineedit.text()) + "$"

        if self.authentication_service.register(questions, plain_key):
            self.warning_label.setStyleSheet("color: #049c84")
            self.warning_label.setText("Account has been registered.")
            self.submit_btn.setEnabled(False)

            data = self.authentication_service.get_session_stored()

            self.info_panel.update_client_status("Registration", data["timestamp_register"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

            self.info_panel.update_client_data("Security Questions", ("Security Questions", parse_array(questions)))
            self.info_panel.update_client_data("Answers", ("Answers", plain_key))

            self.info_panel.update_server_data("User Security Questions", ("User Security Questions", parse_array(data["user_questions"])))
            self.info_panel.update_server_data("User Security Answers", ("User Security Answers", byte_str(data["hashed_secret"])))
            self.info_panel.update_server_data("Salt", ("Salt Value", byte_str(data["salt"])))

            self.info_panel.update_data_note(1)

            self.info_panel.log_text(f"Client: {len(questions)} security question selected and all answers entered.")
            self.info_panel.log_text("Client: Sending data through a secure communication channel.")
            self.info_panel.log_text("Server: Hashing the answers to the security questions")
            self.info_panel.log_text("Server: Registering user with security questions and hashed secret.")
            self.info_panel.log_text("Registration successful.\n")

            self.message_service.send(self, "Registered", None)


class SecurityQuestionAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self, info_panel: QWidget) -> None:
        super().__init__("views/authenticate_views/security_question_view.ui", info_panel)
        
        self.answer_widgets = []

        self.submit_btn.clicked.connect(self.send)
        self.warning_label.setVisible(False)
        self.setup_ui()
        self.initalise_infopanel()

        self.frame.adjust_shadow(30, 50, 2, 2)

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

    def initalise_infopanel(self) -> None:
        data = self.authentication_service.get_session_stored()

        self.info_panel.add_client_data("Answers", ("Answers", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Security Questions", ("User Security Questions", parse_array(data["user_questions"])), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Security Answers", ("User Security Answers", byte_str(data["hashed_secret"])), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", byte_str(data["salt"])), InfoMode.EXPAND)

        self.info_panel.log_text("Client: Request to access account.")
        self.info_panel.log_text("Server: Sending security questions of the user to the client.")
        self.info_panel.log_text("Waiting for answers to security questions...\n")

    def authenticated(self, mode: int = 0) -> None:
        self.warning_label.setStyleSheet("color: #049c84")
        self.warning_label.setText("The user has been authenticated.")
        self.submit_btn.setEnabled(False)

        data = self.authentication_service.get_session_stored()

        self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

        if mode: # bypass mode
            self.info_panel.update_client_data("Answers", ("Answers", data["user_answers"]))

        self.info_panel.log_text(f"Client: {len(self.answer_widgets)} security question displayed and all answers entered.")
        self.info_panel.log_text("Client: Sending answers through a secure communication channel.")
        self.info_panel.log_text("Server: Received answers to security questions")
        self.info_panel.log_text("Server: Hashing and salting the received answers")
        self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
        self.info_panel.log_text("Authentication successful.\n")

        self.message_service.send(self, "Authenticated", None)
        

    def send(self) -> None:
        plain_key = ""
        for answer_lineedit in self.answer_widgets:
            plain_key += normalise_text(answer_lineedit.text()) + "$"

        flag = self.authentication_service.authenticate(plain_key)
        if flag == 0:
            self.authenticated()
        else:
            if flag == 1:
                self.warning_label.setText("These credentials does not match our records.")

                self.info_panel.update_client_status("Authentication", self.authentication_service.get_session_stored()["timestamp_authenticate"])
                self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")
                self.info_panel.update_data_note(1)

                self.info_panel.log_text("Client: Sending answers through a secure communication channel.")
                self.info_panel.log_text("Server: Received answers to security questions")
                self.info_panel.log_text("Server: Hashing and salting the received answers")
                self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
                self.info_panel.log_text("Authentication unsuccessful.\n")
            elif flag == 2:
                self.warning_label.setText("Locked for 10 seconds.")

                self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

            self.warning_label.setVisible(True)

        self.info_panel.update_client_data("Answers", ("Answers", plain_key))
