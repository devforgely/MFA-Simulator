import random
import time
from typing import List, Tuple
from enum import Enum
from services.data_service import Badge

class QuizType(Enum):
    CUSTOM = 0
    CLASSIC = 1
    TIMED = 2
    IMPROVEMENT = 3

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
        self.type = QuizType.CUSTOM
        self.quizzes = []
        self.category_quiz = {}

        self.at = -1
        self.to_view = 0
        self.current_answers = []
        self.category_answer = {}
        self.average_difficulty = 0.0
        self.time = 0.0

    def configure(self, new_config: dict) -> None:
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value

    def configure_classic(self) -> None:
        self.type = QuizType.CLASSIC
        self.configure({'num_questions': 10, 'difficulty_range': (1, 10), 'all_categories': True, 'is_timed': False})

    def configure_timed(self) -> None:
        self.type = QuizType.TIMED
        self.configure({'num_questions': 10, 'difficulty_range': (1, 10), 'all_categories': True, 'is_timed': True, 'max_time': 5})

    def configure_improvement(self) -> None:
        self.type = QuizType.IMPROVEMENT
        improvement_categories = [c[0] for c in self.data_service.get_user_improvements()]
        self.configure({'num_questions': 10, 'difficulty_range': (1, 10), 'all_categories': False, 
                        'categories': improvement_categories, 'is_timed': False})

    def generate_quiz(self) -> bool:
        if not self.config['all_categories'] and not self.config['categories']:
            return False
        
        self.at = -1
        self.to_view = 0
        self.average_difficulty = 0.0
        self.category_quiz = {}
        self.category_answer = {}

        filtered_questions = [q for q in self.data_service.get_quiz_bank()["questions"] \
                              if (self.config['all_categories'] or q['category'] in self.config['categories']) and \
                                self.config['difficulty_range'][0] <= int(q['difficulty']) <= self.config['difficulty_range'][1]]

        # Randomly select questions from the filtered list
        self.quizzes = random.sample(filtered_questions, min(self.config['num_questions'], len(filtered_questions)))
        self.current_answers: List[Tuple[str, bool]] = [("", False)] * len(self.quizzes)
        return True
    
    def get_time(self) -> tuple:
        return (self.config['is_timed'], self.config['max_time'])

    def get_quizzes_size(self) -> int:
        return len(self.quizzes)

    def get_quiz(self, direction: int) -> tuple:
        if self.at == -1:
            self.time = time.time()
        
        self.at += direction
        if self.at >= len(self.quizzes):
            self.terminate_quiz()
            return ()
        if self.at < 0:
            self.at = 0
        
        quiz = self.quizzes[self.at]
        if direction > 0:    
            if self.to_view == self.at:
                self.average_difficulty += float(quiz['difficulty'])
                self.category_quiz[quiz['category']] = self.category_quiz.get(quiz['category'], 0) + 1
                self.to_view += 1
                return (self.at+1, quiz, None)
        return (self.at+1, quiz, self.current_answers[self.at][0])
    
    def submit_answer(self, answer: str) -> None:
        if answer:
            if self.quizzes[self.at]["answer"] == answer:
                self.current_answers[self.at] = (answer, True)
            else:
                self.current_answers[self.at] = (answer, False)

    def terminate_quiz(self) -> None:
        self.time = time.time() - self.time

    def quiz_timeout(self) -> None:
        self.terminate_quiz()
        for i in range(self.to_view, len(self.quizzes)):
            self.average_difficulty += float(self.quizzes[i]['difficulty'])
            self.category_quiz[self.quizzes[i]['category']] = self.category_quiz.get(self.quizzes[i]['category'], 0) + 1

    def check_answers(self) -> tuple:
        correct = 0
        for i in range(len(self.current_answers)):
            if self.current_answers[i][1]:
                self.category_answer[self.quizzes[i]['category']] = self.category_answer.get(self.quizzes[i]['category'], 0) + 1
                correct += 1
        
        #BADGE CONDITION
        if len(self.current_answers) >= 20 and correct == len(self.current_answers):
            self.data_service.update_user_badge(Badge.QUIZ_WHIZ)
        #BADGE END
            
        #BADGE CONDITION
        if self.type == QuizType.IMPROVEMENT:
            self.data_service.update_user_badge(Badge.LEARNER)
        #BADGE END
            
        self.data_service.update_user_quiz(correct)

        return (correct, len(self.current_answers))
    
    def check_difficulty(self) -> float:
        self.average_difficulty = round(self.average_difficulty / len(self.quizzes), 1)
        return self.average_difficulty
    
    def check_time(self) -> str:
        # Calculate minutes and seconds
        minutes = int(self.time // 60)
        seconds = int(self.time % 60)
        # Format elapsed time as MM:SS
        return f"{minutes:02d}:{seconds:02d}"
    
    def check_time_per_question(self) -> str:
        time = self.time / len(self.quizzes)
        minutes = int(time // 60)
        seconds = int(time % 60)

        return f"{minutes:02d}:{seconds:02d}"
    
    def get_all_categories(self) -> set:
        return self.data_service.get_quiz_bank()["categories"][:]
    
    def category_analyse(self) -> list:
        percentages = []
        correct_to_incorrect = []
        for category in self.category_quiz:
            total = self.category_quiz[category]
            correct = self.category_answer.get(category, 0)
            percentage = (correct / total) * 100
            percentages.append((category, percentage))
            correct_to_incorrect.append((category, 2*correct-total))

        self.data_service.update_user_improvement(correct_to_incorrect)
        # Sort the list of tuples by the percentage
        percentages.sort(key=lambda x: x[1])
        return percentages
