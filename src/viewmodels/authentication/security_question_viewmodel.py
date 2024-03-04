from viewmodels.authentication.authentication_base import *
from services.container import ApplicationContainer
from models.utils import parse_array, byte_str, normalise_text


class SecurityQuestionRegisterViewModel(AuthenticationBaseViewModel):
    add_question_signal = pyqtSignal(list, str, str)
    remove_question_signal = pyqtSignal()
    unselected_changed = pyqtSignal(list)

    def __init__(self) -> None:
        super().__init__()

        self.MINIMUM_QUESTION = 2
        self.MAXIMUM_QUESTION = 5
        
        self.display_details = self.authentication_service.get_display_details()
        self.unselected_question = ApplicationContainer.data_service().get_security_questions()
        self.question_size = 0
        self.questions = []
        self.answer_key = ""
        self.too_short_flag = False

    def add_question(self) -> None:
        if self.question_size < self.MAXIMUM_QUESTION: 
            if self.question_size < self.MINIMUM_QUESTION:
                self.add_question_signal.emit(self.unselected_question, f"Question {self.question_size+1} *", "Answer *")
            else:
                self.add_question_signal.emit(self.unselected_question, f"Question {self.question_size+1}", "Answer")
            self.question_size += 1

    def remove_question(self) -> None:
        if self.question_size > self.MINIMUM_QUESTION:
            self.remove_question_signal.emit()
            self.question_size -= 1

    def recover_unselected_question(self, question: str) -> None:
        self.unselected_question.append(question)
        self.unselected_changed.emit(self.unselected_question)

    def on_question_selected(self, question: str) -> None:
        self.unselected_question.remove(question)
        self.unselected_changed.emit(self.unselected_question)

    def add_security_answer(self, question: str, answer: str) -> None:
        if len(answer) < 3: self.too_short_flag = True
        self.questions.append(question)
        self.answer_key += normalise_text(answer) + "$"

    def clear_security_answer(self) -> None:
        self.questions = []
        self.answer_key = ""

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["user_questions"] = parse_array(data["user_questions"])
        data["hashed_secret"] = byte_str(data["hashed_secret"])
        data["salt"] = byte_str(data["salt"])
        return data
    
    def send(self) -> None:
        if self.too_short_flag:
            self.too_short_flag = False
            self.clear_security_answer()
            self.state_change.emit("Your answer must be atleast three characters long and case-sensitive is ignored.", 1)
        elif self.authentication_service.register(self.questions, self.answer_key):
            self.state_change.emit("Account has been registered.", 0)
            self.state_data_change.emit(self.state_data(), 0)
            self.message_service.send(self, "Registered")
        else:
            self.state_change.emit("Registration Fail", 1) 

class SecurityQuestionAuthenticateViewModel(AuthenticationBaseViewModel):
    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        self.answer_size = 0
        self.answer_key = ""
    
    def questions_stored(self) -> list:
        return self.authentication_service.get_session_stored()["user_questions"]
    
    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        data["user_questions"] = parse_array(data["user_questions"])
        data["hashed_secret"] = byte_str(data["hashed_secret"])
        data["salt"] = byte_str(data["salt"])
        return data

    def add_answer(self, answer: str) -> None:
        self.answer_key += normalise_text(answer) + "$"
        self.answer_size += 1

    def send(self) -> None:
        flag = self.authentication_service.authenticate(self.answer_key)
        
        if not flag:
            self.state_change.emit("The user has been authenticated.", flag)
            self.message_service.send(self, "Authenticated")
        elif flag == 1:
            self.state_change.emit("These credentials does not match our records.", flag)
        elif flag == 2:
            self.state_change.emit("Locked for 10 seconds.", flag)
        
        self.state_data_change.emit(self.state_data(), flag)
        self.answer_key = ""
        self.answer_size = 0
        
    def bypass(self) -> None:
        self.state_data_change.emit(self.state_data(), 0)
