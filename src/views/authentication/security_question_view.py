from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QGroupBox, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt
from configuration.app_configuration import Settings
from widgets.info_panel import InfoMode

# pyright: reportAttributeAccessIssue=false

class CustemComboBox(QComboBox):
    def __init__(self, parent = None):
        super(CustemComboBox,self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, e):
        e.ignore()
        pass

class SecurityQuestionRegisterView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/register_views/security_question_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.add_question_signal.connect(self.add_question)
        self._viewmodel.remove_question_signal.connect(self.remove_question)
        self._viewmodel.unselected_changed.connect(self.update_combo_boxes)

        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.add_question_btn.clicked.connect(self._viewmodel.add_question)
        self.remove_btn.clicked.connect(self._viewmodel.remove_question)
        self.submit_btn.clicked.connect(self.send)

        self.question_view.layout().addStretch()

        # default minimum security questions
        for _ in range(self._viewmodel.MINIMUM_QUESTION):
            self._viewmodel.add_question()

        self.frame.adjust_shadow(30, 50, 2, 2)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_advantages(self._viewmodel.display_details["advantages"])
        self.info_panel.add_disadvantages(self._viewmodel.display_details["disadvantages"])

        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        self.info_panel.add_client_data("Security Questions", ("Security Questions", "[]"), InfoMode.EXPAND)
        self.info_panel.add_client_data("Answers", ("Answers", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Security Questions", ("User Security Questions", "[]"), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Security Answers", ("User Security Answers", "NULL"), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", "NULL"), InfoMode.EXPAND)

        self.info_panel.log_text("Server: Generate a set of security questions and send to client.")
        self.info_panel.log_text("Waiting for security questions and answers...\n")
        self.info_panel.set_measure_level(40)

    def add_question(self, unselected_questions: list, question_count: str, answer_count: str):
        layout = self.question_view.layout()

        combo_box = CustemComboBox()
        combo_box.currentTextChanged.connect(self._viewmodel.on_question_selected)

        combo_box.setCursor(Qt.PointingHandCursor)
        combo_box.setStyleSheet(f"""
            QComboBox::down-arrow {{
                image: url({Settings.ICON_FILE_PATH}down-arrow.svg);
                padding: 0px 24px 10px 0px;
            }}
        """)

        answer_lineedit = QLineEdit()

        group_question = QGroupBox(question_count)
        group_answer = QGroupBox(answer_count)

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

        # add selections after widgets is placed inside the layout
        combo_box.addItems(unselected_questions)
        combo_box.currentIndexChanged.connect(lambda new_index: self.handle_index_changed(combo_box, new_index))

    def remove_question(self) -> None:
        # delete lineedit with groupbox
        item = self.question_view.layout().takeAt(self.question_view.layout().count() - 2) # account for stretch
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

        # delete combobox with groupbox
        item = self.question_view.layout().takeAt(self.question_view.layout().count() - 2) # account for stretch
        widget = item.widget()
        if widget is not None:
            self._viewmodel.recover_unselected_question(widget.layout().itemAt(0).widget().currentText())
            widget.deleteLater()

    def handle_index_changed(self, combo_box: QComboBox, new_index: int) -> None:
        old_text = combo_box.property("prevText")
        if old_text:
            self._viewmodel.recover_unselected_question(old_text)
        else:
            self._viewmodel.recover_unselected_question(combo_box.itemText(0))
        
        combo_box.setProperty("prevText", combo_box.itemText(new_index))

    def update_combo_boxes(self, unselected_questions: list) -> None:
        # update other combo boxes to exclude the selected option
        layout = self.question_view.layout()

        # must account for the stretch
        for i in range(0, layout.count()-1, 2):
            combo_box = layout.itemAt(i).widget().layout().itemAt(0).widget()
            current_text = combo_box.currentText()
            combo_box.blockSignals(True)
            combo_box.clear()

            combo_box.addItem(current_text)
            combo_box.addItems(unselected_questions)
            combo_box.blockSignals(False)

    def send(self) -> None:
        layout = self.question_view.layout()

        # must account for the stretch
        for i in range(0, layout.count()-1, 2):
            question_box = layout.itemAt(i).widget().layout().itemAt(0).widget()
            answer_lineedit = layout.itemAt(i+1).widget().layout().itemAt(0).widget()
            self._viewmodel.add_security_answer(question_box.currentText(), answer_lineedit.text())
        self._viewmodel.send()
        
    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
            self.add_question_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
        else:
            self.warning_label.setStyleSheet("color: #d5786c;")

        self.warning_label.setText(content)

    def update_data(self, data: dict, flag: int) -> None:
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])

        self.info_panel.update_client_status("Registration", data["timestamp_register"])
        self.info_panel.update_server_status("ACCEPTED", "202", "User Registered")

        self.info_panel.update_client_data("Security Questions", ("Security Questions", data["user_questions"]))
        self.info_panel.update_client_data("Answers", ("Answers", data["user_answers"]))

        self.info_panel.update_server_data("User Security Questions", ("User Security Questions", data["user_questions"]))
        self.info_panel.update_server_data("User Security Answers", ("User Security Answers", data["hashed_secret"]))
        self.info_panel.update_server_data("Salt", ("Salt Value", data["salt"]))

        self.info_panel.log_text(f"Client: {self._viewmodel.question_size} security question selected and all answers entered.")
        self.info_panel.log_text("Client: Sending data through a secure communication channel.")
        self.info_panel.log_text("Server: Hashing the answers to the security questions")
        self.info_panel.log_text("Server: Registering user with security questions and hashed secret.")
        self.info_panel.log_text("Registration successful.\n")


class SecurityQuestionAuthenticateView(QWidget):
    def __init__(self, viewmodel, info_panel, parent: QWidget, ui="views_ui/authenticate_views/security_question_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self.info_panel = info_panel
        self._viewmodel.state_change.connect(self.update_state)
        self._viewmodel.state_data_change.connect(self.update_data)

        self.answer_widgets = []

        self.setup_ui()
    
    def setup_ui(self) -> None:
        self.submit_btn.clicked.connect(self.send)
        self.warning_label.setVisible(False)

        stored = self._viewmodel.questions_stored()
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

        self.frame.adjust_shadow(30, 50, 2, 2)
        self.initalise_infopanel()

    def initalise_infopanel(self) -> None:
        self.info_panel.add_authenticator_description(self._viewmodel.display_details["description"])
        self.info_panel.add_about(self._viewmodel.display_details["usability"])
        self.info_panel.update_method_note(self._viewmodel.display_details["notes"][0])

        data = self._viewmodel.state_data()
        
        self.info_panel.add_client_data("Answers", ("Answers", "NULL"), InfoMode.EXPAND)
        
        self.info_panel.add_server_data("User Security Questions", ("User Security Questions", data["user_questions"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("User Security Answers", ("User Security Answers", data["hashed_secret"]), InfoMode.EXPAND)
        self.info_panel.add_server_data("Salt", ("Salt Value", data["salt"]), InfoMode.EXPAND)

        self.info_panel.log_text("Client: Request to access account.")
        self.info_panel.log_text("Server: Sending security questions of the user to the client.")
        self.info_panel.log_text("Waiting for answers to security questions...\n")

    def send(self) -> None:
        for answer_lineedit in self.answer_widgets:
            self._viewmodel.add_answer(answer_lineedit.text())

        self._viewmodel.send()

    def update_state(self, content: str, flag: int) -> None:
        if not flag:
            self.warning_label.setStyleSheet("color: #049c84")
            self.submit_btn.setEnabled(False)
        
        self.warning_label.setText(content)
        self.warning_label.setVisible(True)

    def update_data(self, data: dict, flag: int) -> None:
        if not flag:
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("ACCEPTED", "202", "User Authenticated")

            self.info_panel.log_text(f"Client: {self._viewmodel.answer_size} security question displayed and all answers entered.")
            self.info_panel.log_text("Client: Sending answers through a secure communication channel.")
            self.info_panel.log_text("Server: Received answers to security questions")
            self.info_panel.log_text("Server: Hashing and salting the received answers")
            self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
            self.info_panel.log_text("Authentication successful.\n")
        elif flag == 1:
            self.info_panel.update_method_note(self._viewmodel.display_details["notes"][1])
            self.info_panel.update_client_status("Authentication", data["timestamp_authenticate"])
            self.info_panel.update_server_status("REJECTED", "406", "User Not Authenticated")

            self.info_panel.log_text("Client: Sending answers through a secure communication channel.")
            self.info_panel.log_text("Server: Received answers to security questions")
            self.info_panel.log_text("Server: Hashing and salting the received answers")
            self.info_panel.log_text("Server: Verifying user by comparing the stored hash with the newly computed hash.")
            self.info_panel.log_text("Authentication unsuccessful.\n")
        elif flag == 2:
            self.info_panel.log_text("Locking authentication for 10 seconds due to multiple fail attempts.\n")

        self.info_panel.update_client_data("Answers", ("Answers", data["answers"]))
    
    def bypass(self) -> None:
        self._viewmodel.bypass()


