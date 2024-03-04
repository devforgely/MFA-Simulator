from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget, QPushButton, QListWidgetItem, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QProgressBar
from PyQt5.QtCore import Qt, QPointF, QRegExp
from PyQt5.QtWidgets import QWidget, QButtonGroup
from PyQt5.QtGui import QColor, QPainter, QIcon, QIntValidator, QRegExpValidator, QPixmap
from configuration.app_configuration import Settings
from viewmodels.quiz_viewmodels import *

# pyright: reportAttributeAccessIssue=false

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
                border: 1px solid #049c84;
                background-color: #94d56c;       
            }
        """)

class Arrow(QWidget):
        def __init__(self, parent=None, collapsed=False):
            QWidget.__init__(self, parent=parent)

            self.setMaximumSize(24, 24)

            # horizontal == 0
            self.arrow_horizontal = (QPointF(2.0, 8.0), QPointF(22.0, 8.0), QPointF(12.0, 18.0))
    
            # vertical == 1
            self.arrow_vertical = (QPointF(8.0, 2.0), QPointF(18.0, 12.0), QPointF(8.0, 22.0))
            # arrow
            self.arrow = None
            self.set_arrow(collapsed)

        def set_arrow(self, arrow_dir):
            if arrow_dir:
                self.arrow = self.arrow_horizontal
            else:
                self.arrow = self.arrow_vertical
            self.update()

        def paintEvent(self, event):
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QColor(64, 64, 64))
            painter.setPen(QColor(64, 64, 64))
            painter.drawPolygon(*self.arrow)
            painter.end()


class QuizView(QStackedWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)

        self._viewmodel = viewmodel

        self.quiz_settings_page = QuizSettingsView(QuizSettingsViewModel(), parent=self)
        self.quiz_play_page = QuizPlayView(QuizPlayViewModel(), parent=self)
        self.quiz_response_page = QuizResponseView(QuizResponseViewModel(), parent=self)
        self.addWidget(self.quiz_settings_page)
        self.addWidget(self.quiz_play_page)
        self.addWidget(self.quiz_response_page)

        self._viewmodel.view_quiz.connect(lambda: self.setCurrentWidget(self.quiz_play_page))
        self._viewmodel.view_response.connect(lambda: self.setCurrentWidget(self.quiz_response_page))
        self._viewmodel.view_setting.connect(lambda: self.setCurrentWidget(self.quiz_settings_page))


class QuizSettingsView(QWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/quiz_settings_view.ui", self)

        self._viewmodel = viewmodel
        self._viewmodel.custom_setting_expand_changed.connect(self.update_setting_expand)
        self._viewmodel.category_list_changed.connect(self.update_category_combobox)

        self.setup_ui()

        self._viewmodel.custom_setting_expand()
        self._viewmodel.quiz_categories()

    def setup_ui(self) -> None:
        sp_retain = self.config_box.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.config_box.setSizePolicy(sp_retain)

        self.arrow = Arrow(collapsed=False)
        self.collapsable_frame.layout().insertWidget(0, self.arrow)

        self.num_field.setValidator(QIntValidator())
        self.time_field.setValidator(QIntValidator())
        self.difficulty_field.setValidator(QRegExpValidator(QRegExp("[1-9]-[0-9]*")))

        self.classic_btn.clicked.connect(self.set_quiz)
        self.timed_btn.clicked.connect(self.set_quiz)
        self.improvement_btn.clicked.connect(self.set_quiz)
        self.amend_btn.clicked.connect(self.set_quiz)

        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.prepare_quiz)

        self.collapsable_frame.clicked.connect(lambda: self.update_setting_expand(not self.config_box.isVisible()))

        self.all_categories_box.stateChanged.connect(self.change_all_categories)
        self.timed_box.stateChanged.connect(self.change_timed)

        self.retain_size(self.category_label)
        self.retain_size(self.category_combobox)
        self.retain_size(self.add_category_label)
        self.retain_size(self.category_list)

        self.change_all_categories()
        self.change_timed()
        self.setting_warning.setVisible(False)

    def update_setting_expand(self, state: bool):
        self.config_box.setVisible(state)
        self.amend_btn.setVisible(state)
        self.arrow.set_arrow(state)

    def set_quiz(self) -> None:
        btn_name = self.sender().objectName()

        match(btn_name):
            case "classic_btn":
                self._viewmodel.set_classic()
                self.quiz_note.setText("""<b>Classic Quiz</b>: This is a standard quiz type.<br>
                                       <p>It consists of 10 questions that cover all categories and difficulty ranges.</p>
                                       <p>There is no time limit for this quiz, so you can take your time to think through each question.</p>""")
            case "timed_btn":
                self._viewmodel.set_timed()
                self.quiz_note.setText("""<b>Timed Quiz</b>: This quiz is similar to the Classic Quiz.<br>
                                       <p>It includes 10 questions from all categories and difficulty ranges.</p>
                                       <p>However, it adds an element of time pressure.</p>
                                       <p>You have a maximum of 5 minutes to complete the entire quiz.</p>
                                       <p>This format tests not only your knowledge but also your ability to think quickly.</p>""")
            case "improvement_btn":
                self._viewmodel.set_improvement()
                self.quiz_note.setText("""<b>Improvement Quiz</b>: This quiz is designed to help you improve in areas where you're not doing well.<br>
                                       <p>It includes 10 questions from the categories you've struggled with in the past, across all difficulty ranges.</p>
                                       <p>Like the Classic Quiz, there is no time limit, so you can focus on understanding the questions and improving your knowledge.</p>""")
            case "amend_btn":
                if self._viewmodel.validate_quiz_setting(self.difficulty_field.text(), self.num_field.text(), self.all_categories_box.isChecked(),
                                                         self.get_list_categories(), self.timed_box.isChecked(), self.time_field.text()):
                    self.setting_warning.setVisible(False)
                    self.quiz_note.setText("""<b>Custom Quiz</b>: This quiz format offers the highest level of personalisation.<br>
                                        <p>You have the freedom to set the number of questions, choose the categories, specify the difficulty range, and decide whether it's timed or not.</p>
                                        <p>If you choose a timed quiz, you can also set the maximum time limit.</p>
                                        <p>This format allows you to tailor the quiz to your specific needs and preferences, making it a great option for focused learning or practice.</p>""")
                else:
                    self.setting_warning.setVisible(True)
            case _:
                Exception("Undefined Button Behaviour")
        self.start_btn.setEnabled(True)

    def prepare_quiz(self) -> None:
        if not self._viewmodel.prepare_quiz():
            self.quiz_note.setText("""<b>Fail to generate quiz.</b><br>
                                   <p>Perhaps you need to try complete a classic quiz so we can see what you can improve on.</p>""")
            
    def change_all_categories(self) -> None:
        if self.all_categories_box.isChecked():
            self.category_label.setVisible(False)
            self.category_combobox.setVisible(False)
            self.add_category_label.setVisible(False)
            self.category_list.setVisible(False)
        else:
            self.category_label.setVisible(True)
            self.category_combobox.setVisible(True)
            self.add_category_label.setVisible(True)
            self.category_list.setVisible(True)

    def change_timed(self) -> None:
        if self.timed_box.isChecked():
            self.time_label.setVisible(True)
            self.time_field.setVisible(True)
        else:
            self.time_label.setVisible(False)
            self.time_field.setVisible(False)
    
    def is_text_in_list(self, text: str) -> bool:
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            widget = self.category_list.itemWidget(item)
            label = widget.findChild(QLabel)
            if label.text() == text:
                return True
        return False
    
    def get_list_categories(self) -> list:
        list = []
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            widget = self.category_list.itemWidget(item)
            label = widget.findChild(QLabel)
            list.append(label.text())
        return list

    def check_and_add_category(self) -> None:
        current_text = self.category_combobox.currentText()
        if not self.is_text_in_list(current_text):
            item = QListWidgetItem(self.category_list)

            widget = QWidget()
            layout = QHBoxLayout(widget)
            label = QLabel(current_text)
            label.setStyleSheet("font-size: 9pt; font-weight: normal;")
            button = QPushButton()
            button.setIcon(QIcon(Settings.ICON_FILE_PATH + "cross.svg"))
            button.clicked.connect(lambda: self.delete_item(item))

            layout.addWidget(label)
            layout.addWidget(button)

            item.setSizeHint(widget.sizeHint())

            self.category_list.addItem(item)
            self.category_list.setItemWidget(item, widget)
    
    def delete_item(self, item):
        row = self.category_list.row(item)
        self.category_list.takeItem(row)

    def update_category_combobox(self, category_list: list) -> None:
        self.category_combobox.addItems(category_list)
        self.category_combobox.setCurrentIndex(-1)
        self.category_combobox.currentIndexChanged.connect(self.check_and_add_category)

    def retain_size(self, widget) -> None:
        sp_retain = widget.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        widget.setSizePolicy(sp_retain)


class QuizPlayView(QWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/quiz_view.ui", self)

        self._viewmodel = viewmodel
        self._viewmodel.time_mode_changed.connect(self.set_timed)
        self._viewmodel.time_changed.connect(self.update_time_bar)
        self._viewmodel.time_color_changed.connect(self.update_time_bar_color)
        self._viewmodel.quiz_changed.connect(self.update_quiz)

        self.setup_ui()

    def setup_ui(self) -> None:
        self.button_group = QButtonGroup()

        self.next_btn.clicked.connect(self._viewmodel.next_quiz)
        self.backward_btn.clicked.connect(self._viewmodel.quiz_before)

    def set_timed(self, timed: bool, duration: int, max_thread_val: int) -> None:
        if timed:
            self.time_bar.setMaximum(max_thread_val)
            self.time_bar.setStyleSheet("#time_bar::chunk { background-color: #0b69e5; }")
            self.time_label.setText(f"  {duration}:{0:02d}")

            self.time_bar.setVisible(True)
            self.time_label.setVisible(True)
        else:
            self.time_bar.setVisible(False)
            self.time_label.setVisible(False)

    def update_time_bar(self, val: int, mins: int, sec: int) -> None:
        self.time_bar.setValue(val)
        self.time_bar.update()

        self.time_label.setText(f"  {mins}:{sec:02d}")
        self.time_label.update()

    def update_time_bar_color(self, color: str):
        self.time_bar.setStyleSheet(f"#time_bar::chunk {{ background-color: {color}; }}")

    def update_quiz(self, quiz: tuple, quiz_count: int) -> None:
        self.question_label.setText(str(quiz[0])+". "+quiz[1]["question"])
        
        # clear layout for new choices
        for i in reversed(range(self.choices_layout.count())):
                self.choices_layout.itemAt(i).widget().deleteLater()
        for button in self.button_group.buttons():
            self.button_group.removeButton(button)
            button.deleteLater()

        # add button for each choice
        for choice in quiz[1]["choices"]:
            choice_button = QuizButton(choice)
            choice_button.clicked.connect(lambda checked, c=choice: self._viewmodel.save_choice(c))
            self.button_group.addButton(choice_button)
            self.choices_layout.addWidget(choice_button)

            if quiz[2] and choice_button.text() == quiz[2]:
                choice_button.setChecked(True)

        self.progress_label.setText(f"<b>{str(quiz[0])}</b> of <b>{str(quiz_count)}</b> Questions")

        if quiz[0] == quiz_count:
            self.next_btn.setText("Complete Quiz")
        else:
            self.next_btn.setText("Next Question")

        if quiz[0] == 1:
            self.backward_btn.setEnabled(False)
        else:
            self.backward_btn.setEnabled(True)
            

class QuizResponseView(QWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/quiz_response_view.ui", self)

        self._viewmodel = viewmodel
        self._viewmodel.check_time_changed.connect(self.update_time)
        self._viewmodel.time_per_question_changed.connect(self.update_time_per_question)
        self._viewmodel.difficulty_changed.connect(self.update_difficulty)
        self._viewmodel.score_changed.connect(self.update_score)
        self._viewmodel.quiz_detail_changed.connect(self.update_detail_view)

        self.setup_ui()

    def setup_ui(self) -> None:
        self.result_bar.setFixedSize(150, 150)
        self.result_bar.setFormat('%p%|%v / %m')
        self.result_bar.setBrushColor(QColor(77,186,124))

        self.back_btn.clicked.connect(self._viewmodel.back)

    def set_rank(self, percentage: float) -> None:
        if percentage >= 0.6:
            self.result_icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH + "Check-Square--Streamline-Core.svg"))
            self.score_label.setText("Test Passed")
            self.score_label.setStyleSheet("color: #52c17e")
        else:
            self.result_icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH + "Subtract-Square--Streamline-Core.svg"))
            self.score_label.setText("Test Failed")
            self.score_label.setStyleSheet("color: #c15252")

        if percentage >= 0.9:
            self.grade_text.setText("Excellent")
            self.grade_message.setText("You've mastered the material!")
        elif percentage >= 0.8:
            self.grade_text.setText("Great")
            self.grade_message.setText("You've understood most of the material.")
        elif percentage >= 0.7:
            self.grade_text.setText("Good")
            self.grade_message.setText("You've grasped the basic concepts.")
        elif percentage >= 0.6:
            self.grade_text.setText("Pass")
            self.grade_message.setText("You've passed, but there's room for improvement.")
        else:
            self.grade_text.setText("Fail")
            self.grade_message.setText("You might need to study a bit more.")


    def update_time(self, timed: bool, duration: int, result: str) -> None:
        if timed:
            self.time_val.setText(result+f"<font color='#7c7c7c'>&nbsp;&nbsp;/&nbsp;&nbsp;{duration:02d}:00</font>")
        else:
            self.time_val.setText(result)

    def update_time_per_question(self, result: str) -> None:
        self.time_q_label.setText(result)

    def update_difficulty(self, difficulty: str) -> None:
        self.difficulty_float.setText(difficulty)

    def update_score(self, correct: int, total: int) -> None:
        self.set_rank(correct / total)
        self.result_bar.setRange(0, total)
        self.result_bar.setValue(correct)

    
    def update_detail_view(self, quizzes, answers, analyse) -> None:
        # clear question_content
        layout = self.question_content.layout()
        for i in reversed(range(layout.count())): 
            item = layout.takeAt(i)
            if item.widget() is not None:
                item.widget().deleteLater()

        i = 0
        for quiz in quizzes:
            group_widget = QWidget()
            group_layout = QVBoxLayout(group_widget)
            group_layout.setAlignment(Qt.AlignLeft)

            question_label = QLabel(str(i+1)+". "+quiz['question'])
            question_label.setStyleSheet("font-weight: bold")
            group_layout.addWidget(question_label)

            for choice in quiz['choices']:
                choice_widget = QWidget()
                choice_layout = QHBoxLayout(choice_widget)
                choice_layout.setContentsMargins(20, 0, 0, 0)
                choice_layout.setAlignment(Qt.AlignLeft)

                choice_label = QLabel(choice)
                choice_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
                choice_layout.addWidget(choice_label)

                if choice == quiz['answer']: 
                    icon = QLabel()
                    icon.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
                    icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH + "check.svg"))
                    choice_layout.addWidget(icon)

                if choice == answers[i][0]:
                    if answers[i][1]:
                        choice_label.setStyleSheet("border: 1px solid #52c17e;")
                    else:
                        choice_label.setStyleSheet("border: 1px solid #c15252;")
                group_layout.addWidget(choice_widget)
            
            layout.addWidget(group_widget)
            i += 1
        layout.addStretch()

        layout = self.percentage_display.layout()
        for i in reversed(range(layout.count())): 
            item = layout.takeAt(i)
            if item.widget() is not None:
                item.widget().deleteLater()

        for category, percentage in analyse:
            category_title = QLabel(category)
            category_title.setStyleSheet("font-weight: bold;")

            percentage_bar = QProgressBar()
            percentage_bar.setMaximum(100)
            percentage_bar.setValue(int(percentage))
            percentage_bar.setFormat("  Correct: %p%")

            layout.addWidget(category_title)
            layout.addWidget(percentage_bar)
        layout.addStretch()
    

    

