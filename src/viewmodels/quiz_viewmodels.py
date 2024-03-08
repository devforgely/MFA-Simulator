from typing import Any
from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer
from services.data_service import DataService
from widgets.timer import TimeDisplayThread


class QuizViewModel(QObject):
    view_quiz = pyqtSignal()
    view_response = pyqtSignal()
    view_setting = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.message_service = ApplicationContainer.message_service()

        self.message_service.subscribe(self, QuizSettingsViewModel, self.on_message)
        self.message_service.subscribe(self, QuizPlayViewModel, self.on_message)
        self.message_service.subscribe(self, QuizResponseViewModel, self.on_message)
    
    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Play Quiz":
            self.view_quiz.emit()
        elif message_title == "Quiz Response":
            self.view_response.emit()
        elif message_title == "Quiz Settings":
            self.view_setting.emit()


class QuizSettingsViewModel(QObject):
    custom_setting_expand_changed = pyqtSignal(bool)
    category_list_changed = pyqtSignal(list)

    def __init__(self) -> None:
        super().__init__()
        
        self.data_service = ApplicationContainer.data_service()
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.list_categories = []

        self.message_service.subscribe(self, DataService, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Update Custom Quiz":
            self.custom_setting_expand_changed.emit(args[0])

    def custom_setting_expand(self) -> None:
        self.custom_setting_expand_changed.emit(self.data_service.get_custom_quiz_setting_expand())

    def quiz_categories(self) -> None:
        self.category_list_changed.emit(self.quiz_service.get_all_categories())

    def set_classic(self) -> None:
        self.quiz_service.configure_classic()

    def set_timed(self) -> None:
        self.quiz_service.configure_timed()

    def set_improvement(self) -> None:
        self.quiz_service.configure_improvement()

    def is_text_in_list(self, text: str) -> bool:
        return text in self.list_categories
    
    def append_category(self, category: str) -> None:
        self.list_categories.append(category)

    def remove_category(self, category: str) -> None:
        self.list_categories.remove(category)

    def validate_quiz_setting(self, difficulty: str, quiz_count: str, all_categories: bool,
                              is_timed: bool, time_length: str) -> bool:
        range = difficulty.split("-")
        if len(range) == 2:
            low = int(range[0])
            high = int(range[1])
            if not quiz_count:
                return False
            nums_q = int(quiz_count)
            
            if low > 0 and high > 0 and high >= low and nums_q > 0:
                dict = {'num_questions': nums_q, 'difficulty_range': (low, high)}

                if all_categories:
                    dict['all_categories'] = True
                else:
                    dict['all_categories'] = False
                    dict['categories'] = self.list_categories
                
                if is_timed:
                    dict['is_timed'] = True
                    time = int(time_length)
                    if time > 0:
                        dict['max_time'] = time
                    else:
                        dict['max_time'] = 5
                else:
                    dict['is_timed'] = False

                self.quiz_service.configure(dict)
                return True
        return False     

    def prepare_quiz(self) -> bool:
        if self.quiz_service.generate_quiz():
            self.message_service.send(self, "Play Quiz")
            return True
        return False


class QuizPlayViewModel(QObject):
    time_mode_changed = pyqtSignal(bool, int, int)
    time_changed = pyqtSignal(int, int, int)
    time_color_changed = pyqtSignal(str)
    quiz_changed = pyqtSignal(tuple, int)

    def __init__(self) -> None:
        super().__init__()
        
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.max_time = 0
        self.yellow_time = 0
        self.red_time = 0
        self.saved_choice = ""
        self.quiz_size = 0

        self.message_service.subscribe(self, QuizSettingsViewModel, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Play Quiz":
            self.quiz_size = self.quiz_service.get_quizzes_size()
            timed, duration = self.quiz_service.get_time()
            
            if timed:
                self.max_time = duration * 60 # in seconds
                self.yellow_time = int(self.max_time * 0.5)
                self.red_time = int(self.max_time * 0.2)

                # thread for timer
                self.threading = TimeDisplayThread(self.max_time)
                self.threading._signal.connect(self.signal_update)
                self.time_mode_changed.emit(timed, duration, self.threading.max_val)
            else:
                self.max_time = 0
                self.time_mode_changed.emit(timed, 0, 0)

            self.quiz_changed.emit(self.quiz_service.get_quiz(1), self.quiz_size)
            self.saved_choice = ""

            if timed:
                self.threading.start()

    def signal_update(self, val: int, mins: int, sec: int):
        if val == self.yellow_time:
            self.time_color_changed.emit("#ffcd27")
        elif val == self.red_time:
            self.time_color_changed.emit("#f44336")       

        self.time_changed.emit(val, mins, sec)

        if val == 0:
            self.quiz_service.quiz_timeout()
            self.message_service.send(self, "Quiz Response")

    def save_choice(self, choice: str) -> None:
        self.saved_choice = choice

    def next_quiz(self) -> None:
        self.quiz_service.sumbit_answer(self.saved_choice)

        quiz = self.quiz_service.get_quiz(1)
        if quiz:
            self.quiz_changed.emit(quiz, self.quiz_size)
            self.saved_choice = ""
        else:
            if self.max_time != 0:
                self.threading.stop()
            self.message_service.send(self, "Quiz Response")

    def quiz_before(self) -> None:
        self.quiz_changed.emit(self.quiz_service.get_quiz(-1), self.quiz_size)


class QuizResponseViewModel(QObject):
    check_time_changed = pyqtSignal(bool, int, str)
    time_per_question_changed = pyqtSignal(str)
    difficulty_changed = pyqtSignal(str)
    score_changed = pyqtSignal(int, int)
    quiz_detail_changed = pyqtSignal(list, list, list)

    def __init__(self) -> None:
        super().__init__()
        
        self.quiz_service = ApplicationContainer.quiz_service()
        self.message_service = ApplicationContainer.message_service()

        self.message_service.subscribe(self, QuizPlayViewModel, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Quiz Response":
            timed, duration = self.quiz_service.get_time()
            self.check_time_changed.emit(timed, duration, self.quiz_service.check_time())

            self.time_per_question_changed.emit(self.quiz_service.check_time_per_question())
            self.difficulty_changed.emit(str(self.quiz_service.check_difficulty()))

            correct, total = self.quiz_service.check_answers()
            self.score_changed.emit(correct, total)

            self.quiz_detail_changed.emit(self.quiz_service.quizzes, self.quiz_service.current_answers, self.quiz_service.category_analyse())

    def back(self) -> None:
        self.message_service.send(self, "Quiz Settings")