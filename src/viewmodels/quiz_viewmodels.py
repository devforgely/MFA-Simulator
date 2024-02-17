from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QStackedWidget, QPushButton, QListWidgetItem, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QProgressBar
from PyQt5.QtCore import Qt, QPointF, QRegExp
from PyQt5.QtWidgets import QWidget, QButtonGroup
from PyQt5.QtGui import QColor, QPainter, QIcon, QIntValidator, QRegExpValidator, QPixmap
from widgets.timer import TimeDisplayThread
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from data.data_service import DataService

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
                self.arrow = self.arrow_vertical
            else:
                self.arrow = self.arrow_horizontal

        def paintEvent(self, event):
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QColor(64, 64, 64))
            painter.setPen(QColor(64, 64, 64))
            painter.drawPolygon(*self.arrow)
            painter.end()

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
            self.quiz_play_page.setTimed(args[0])
            self.quiz_play_page.start_quiz()
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
        self.data_service = ApplicationContainer.data_service()
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.is_collasped = not self.data_service.get_custom_quiz_expand()

        self.config_box.setVisible(not self.is_collasped)
        self.amend_btn.setVisible(not self.is_collasped)
        self.arrow = Arrow(collapsed=self.is_collasped)
        self.collapsable_frame.layout().insertWidget(0, self.arrow)

        self.num_field.setValidator(QIntValidator())
        self.time_field.setValidator(QIntValidator())
        self.difficulty_field.setValidator(QRegExpValidator(QRegExp("[1-9]-[0-9]*")))

        self.classic_btn.clicked.connect(self.set_quiz)
        self.timed_btn.clicked.connect(self.set_quiz)
        self.improvement_btn.clicked.connect(self.set_quiz)
        self.amend_btn.clicked.connect(self.set_quiz)

        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_quiz)
        self.collapsable_frame.clicked.connect(self.toggle_collapse)

        self.all_categories_box.stateChanged.connect(self.change_all_categories)
        self.timed_box.stateChanged.connect(self.change_timed)

        self.category_combobox.addItems(self.quiz_service.get_all_categories())
        self.category_combobox.setCurrentIndex(-1)
        self.category_combobox.currentIndexChanged.connect(self.check_and_add_category)

        self.retain_size(self.category_label)
        self.retain_size(self.category_combobox)
        self.retain_size(self.add_category_label)
        self.retain_size(self.category_list)

        self.change_all_categories()
        self.change_timed()
        self.setting_warning.setVisible(False)

        self.message_service.subscribe(self, DataService, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Update custom quiz":
            self.is_collasped = args[0]
            self.toggle_collapse()
    
    def set_quiz(self) -> None:
        btn_name = self.sender().objectName()

        match(btn_name):
            case "classic_btn":
                self.quiz_service.configure_classic()
                self.quiz_note.setText("""<b>Classic Quiz</b>: This is a standard quiz type.<br>
                                       <p>It consists of 10 questions that cover all categories and difficulty ranges.</p>
                                       <p>There is no time limit for this quiz, so you can take your time to think through each question.</p>""")
            case "timed_btn":
                self.quiz_service.configure_timed()
                self.quiz_note.setText("""<b>Timed Quiz</b>: This quiz is similar to the Classic Quiz.<br>
                                       <p>It includes 10 questions from all categories and difficulty ranges.</p>
                                       <p>However, it adds an element of time pressure.</p>
                                       <p>You have a maximum of 5 minutes to complete the entire quiz.</p>
                                       <p>This format tests not only your knowledge but also your ability to think quickly.</p>""")
            case "improvement_btn":
                self.quiz_service.configure_improvement()
                self.quiz_note.setText("""<b>Improvement Quiz</b>: This quiz is designed to help you improve in areas where you're not doing well.<br>
                                       <p>It includes 10 questions from the categories you've struggled with in the past, across all difficulty ranges.</p>
                                       <p>Like the Classic Quiz, there is no time limit, so you can focus on understanding the questions and improving your knowledge.</p>""")
            case "amend_btn":
                settings = self.validate_quiz_setting()
                if settings:
                    self.setting_warning.setVisible(False)
                    self.quiz_service.configure(settings)
                    self.quiz_note.setText("""<b>Custom Quiz</b>: This quiz format offers the highest level of personalisation.<br>
                                        <p>You have the freedom to set the number of questions, choose the categories, specify the difficulty range, and decide whether it's timed or not.</p>
                                        <p>If you choose a timed quiz, you can also set the maximum time limit.</p>
                                        <p>This format allows you to tailor the quiz to your specific needs and preferences, making it a great option for focused learning or practice.</p>""")
                else:
                    self.setting_warning.setVisible(True)
            case _:
                Exception("Undefined Button Behaviour")
        self.start_btn.setEnabled(True)

    def start_quiz(self) -> None:
        if self.quiz_service.generate_quiz():
            self.message_service.send(self, "Play Quiz", self.quiz_service.get_time())
        else:
            self.quiz_note.setText("""<b>Fail to generate quiz.</b><br>
                                   <p>Perhaps you need to try complete a classic quiz so we can see what you can improve on.</p>""")

    def toggle_collapse(self) -> None:
        self.config_box.setVisible(self.is_collasped)
        self.amend_btn.setVisible(self.is_collasped)
        self.is_collasped = not self.is_collasped
        self.arrow.set_arrow(self.is_collasped)
        self.arrow.update()

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

    def validate_quiz_setting(self) -> dict:
        range = self.difficulty_field.text().split("-")
        if len(range) <= 1:
            return {}
        
        low = int(range[0])
        high = int(range[1])
        nums_q = int(self.num_field.text())
        
        if low > 0 and high > 0 and high >= low and nums_q > 0:
            dict = {'num_questions': nums_q, 'difficulty_range': (low, high)}

            if self.all_categories_box.isChecked():
                dict['all_categories'] = True
            else:
                dict['all_categories'] = False
                dict['categories'] = self.get_list_categories()
            
            if self.timed_box.isChecked():
                dict['is_timed'] = True
                time = int(self.time_field.text())
                if time > 0:
                    dict['max_time'] = time
                else:
                    dict['max_time'] = 5
            else:
                dict['is_timed'] = False

            return dict
        return {}      

    def retain_size(self, widget) -> None:
        sp_retain = widget.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        widget.setSizePolicy(sp_retain)
        


class QuizPlayViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.max_time = 0
        self.yellow_time = 0
        self.red_time = 0
        self.saved_choice = ""

        self.button_group = QButtonGroup()

        self.next_btn.clicked.connect(self.next_quiz)
        self.backward_btn.clicked.connect(self.quiz_before)
    
    def setTimed(self, timed) -> None:
        if timed[0]:
            self.time_bar.setVisible(True)
            self.time_label.setVisible(True)
            self.max_time = timed[1] * 60 # in seconds
            self.yellow_time = int(self.max_time * 0.4)
            self.red_time = int(self.max_time * 0.2)
            # thread for timer
            self.threading = TimeDisplayThread(self.max_time)
            self.threading._signal.connect(self.signal_update)

            self.time_bar.setMaximum(self.threading.MaxValue())
            self.time_bar.setStyleSheet("#time_bar::chunk { background-color: #0b69e5; }")
            self.time_label.setText(f"  {timed[1]}:{0:02d}")
        else:
            self.max_time = 0
            self.time_bar.setVisible(False)
            self.time_label.setVisible(False)

    def signal_update(self, val: int, mins: int, sec: int):
        if val == self.yellow_time:
            self.time_bar.setStyleSheet("#time_bar::chunk { background-color: #ffcd27; }")
        elif val == self.red_time:
            self.time_bar.setStyleSheet("#time_bar::chunk { background-color: #f44336; }")
        self.time_bar.setValue(val)
        self.time_bar.update()

        self.time_label.setText(f"  {mins}:{sec:02d}")
        self.time_label.update()

        if val == 0:
            self.quiz_service.terminate_quiz()
            self.message_service.send(self, "Quiz Response", None)

    def save_choice(self, choice) -> None:
        self.saved_choice = choice

    def init_quiz(self, quiz: tuple) -> None:
        if quiz:
            self.question_label.setText(str(quiz[0])+". "+quiz[1]["question"])
            
            for i in reversed(range(self.choices_layout.count())):
                    self.choices_layout.itemAt(i).widget().deleteLater()
            for button in self.button_group.buttons():
                self.button_group.removeButton(button)
                button.deleteLater()

            for choice in quiz[1]["choices"]:
                choice_button = QuizButton(choice)
                choice_button.clicked.connect(lambda checked, c=choice: self.save_choice(c))
                self.button_group.addButton(choice_button)
                self.choices_layout.addWidget(choice_button)

                if quiz[2] and choice_button.text() == quiz[2]:
                    choice_button.setChecked(True)

            self.progress_label.setText(f"<b>{str(quiz[0])}</b> of <b>{str(self.quiz_service.get_quizzes_size())}</b> Questions")

            if quiz[0] == self.quiz_service.get_quizzes_size():
                self.next_btn.setText("Complete Quiz")
            else:
                self.next_btn.setText("Next Question")

            if quiz[0] == 1:
                self.backward_btn.setEnabled(False)
            else:
                self.backward_btn.setEnabled(True)

            self.save_choice("")
        else:
            if self.max_time != 0:
                self.threading.stop()
            self.message_service.send(self, "Quiz Response", None)

    def start_quiz(self) -> None:
        self.init_quiz(self.quiz_service.get_quiz(1))
        if self.max_time != 0:
            self.threading.start()

    def next_quiz(self) -> None:
        self.quiz_service.sumbit_answer(self.saved_choice)
        self.init_quiz(self.quiz_service.get_quiz(1))

    def quiz_before(self) -> None:
        self.init_quiz(self.quiz_service.get_quiz(-1))


class QuizResponseViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/quiz_response_view.ui", self)
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.result_bar.setFixedSize(150, 150)
        self.result_bar.setFormat('%p%|%v / %m')
        self.result_bar.setBrushColor(QColor(77,186,124))

        self.back_btn.clicked.connect(self.back)

    def setup(self) -> None:
        timed = self.quiz_service.get_time()
        if timed[0]:
            self.time_val.setText(self.quiz_service.check_time()+f"<font color='#7c7c7c'>&nbsp;&nbsp;/&nbsp;&nbsp;{timed[1]:02d}:00</font>")
        else:
            self.time_val.setText(self.quiz_service.check_time())
        self.difficulty_float.setText(str(self.quiz_service.check_difficulty()))

        result = self.quiz_service.check_answers()
        self.set_rank(result[0]/result[1])
        self.result_bar.setRange(0, result[1])
        self.result_bar.setValue(result[0])
        

        layout = self.question_content.layout()
        for i in reversed(range(layout.count())): 
            item = layout.takeAt(i)
            if item.widget() is not None:
                item.widget().deleteLater()

        answers = self.quiz_service.get_current_answers()
        i = 0
        for quiz in self.quiz_service.get_quizzies():
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

        for category, percentage in self.quiz_service.category_analyse():
            category_title = QLabel(category)
            category_title.setStyleSheet("font-weight: bold;")

            percentage_bar = QProgressBar()
            percentage_bar.setMaximum(100)
            percentage_bar.setValue(int(percentage))
            percentage_bar.setFormat("  Correct: %p%")

            layout.addWidget(category_title)
            layout.addWidget(percentage_bar)
        layout.addStretch()

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

    def back(self) -> None:
        self.message_service.send(self, "Quiz Settings", None)