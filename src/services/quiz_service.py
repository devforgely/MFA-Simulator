import random
import time
from typing import List, Tuple


class QuizService():
    def __init__(self, data_service) -> None:
        self.data_service = data_service
        self.config = {
            'num_questions': 10,
            'difficulty_range': (1, 10),
            'categories': [],
            'all_categories': True,
            'is_timed': False,
            'max_time': 5
        }
        self.quizzes = []

        self.at = -1
        self.viewed = 0
        self.current_answers = []
        self.average_difficulty = 0.0
        self.time = 0.0

    def configure(self, new_config: dict) -> None:
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value

    def configure_classic(self) -> None:
        self.configure({'num_questions': 10, 'difficulty_range': (1, 10), 'all_categories': True, 'is_timed': False})

    def configure_timed(self) -> None:
        self.configure({'num_questions': 10, 'difficulty_range': (1, 10), 'all_categories': True, 'is_timed': True, 'max_time': 5})

    def configure_improvement(self) -> None:
        improvement_categories = self.data_service.get_user_improvements()[:]
        self.configure({'num_questions': 10, 'difficulty_range': (1, 10), 'all_categories': False, 
                        'categories': improvement_categories, 'is_timed': False})

    def generate_quiz(self) -> bool:
        if not self.config['all_categories'] and not self.config['categories']:
            return False
        
        self.at = -1
        self.viewed = 0
        self.average_difficulty = 0.0

        filtered_questions = [q for q in self.data_service.get_quiz_bank()["questions"] \
                              if (self.config['all_categories'] or q['category'] in self.config['categories']) and \
                                self.config['difficulty_range'][0] <= int(q['difficulty']) <= self.config['difficulty_range'][1]]

        # Randomly select questions from the filtered list
        self.quizzes = random.sample(filtered_questions, min(self.config['num_questions'], len(filtered_questions)))
        self.current_answers: List[Tuple[str, bool]] = [(str(""), False)] * len(self.quizzes)
        return True
    
    def get_time(self) -> tuple:
        return (self.config['is_timed'], self.config['max_time'])

    def get_quizzes_size(self) -> int:
        return len(self.quizzes)

    def get_quiz(self, direction: int) -> tuple:
        if self.at == -1:
            self.time = time.time()
        
        self.at += direction
        if self.at == len(self.quizzes):
            self.terminate_quiz()
            return ()
        
        quiz = self.quizzes[self.at]
        if direction == 1:    
            if self.viewed <= self.at:
                self.average_difficulty += float(quiz['difficulty'])
                self.viewed += 1
                return (self.at+1, quiz, None)
            else:
                return (self.at+1, quiz, self.current_answers[self.at][0])
        else:
            return (self.at+1, quiz, self.current_answers[self.at][0])
    
    def sumbit_answer(self, answer: str) -> None:
        if self.quizzes[self.at]["answer"] == answer:
            self.current_answers[self.at] = (answer, True)
        else:
            self.current_answers[self.at] = (answer, False)

    def terminate_quiz(self) -> None:
        self.time = time.time() - self.time
        self.data_service.update_user_quiz()

    def quiz_timeout(self) -> None:
        self.terminate_quiz()
        self.average_difficulty = 0
        for quiz in self.quizzes:
            self.average_difficulty += float(quiz['difficulty'])

    def check_answers(self) -> tuple:
        correct = 0
        for _, bool in self.current_answers:
            if bool:
                correct += 1
        return (correct, len(self.current_answers))
    
    def check_difficulty(self) -> float:
        self.average_difficulty = round(self.average_difficulty / len(self.quizzes), 1)
        return self.average_difficulty
    
    def check_time(self) -> str:
        # Calculate minutes and seconds
        minutes = int(self.time // 60)
        seconds = int(self.time % 60)
        # Format elapsed time as M:SS
        return f"{minutes}:{seconds:02d}"
    
    def get_all_categories(self) -> set:
        return self.data_service.get_quiz_bank()["categories"]
