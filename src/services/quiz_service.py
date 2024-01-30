import random
import time


class QuizService():
    def __init__(self, data_service) -> None:
        self.data_service = data_service
        self.num_questions = 3
        self.difficulty_range = (1, 10)
        self.categories = []
        self.all_categories = True
        self.is_timed = False
        self.max_time = 5
        self.quizzes = []

        self.current_answers = []
        self.average_difficulty = 0.0
        self.time = 0.0

    def generate_quiz(self):
        filtered_questions = [q for q in self.data_service.get_quiz_bank() \
                              if (self.all_categories or q['category'] in self.categories) and int(q['difficulty']) \
                                in range(self.difficulty_range[0], self.difficulty_range[1] + 1)]

        # Randomly select questions from the filtered list
        self.quizzes = random.sample(filtered_questions, min(self.num_questions, len(filtered_questions)))

    def get_quizzes_size(self) -> int:
        return len(self.quizzes)

    def get_quiz(self) -> tuple:
        if len(self.current_answers) >= len(self.quizzes):
            self.time = time.time() - self.time
            return ()
        
        quiz = self.quizzes[len(self.current_answers)]
        self.average_difficulty += float(quiz['difficulty'])
        self.time = time.time()
        return (len(self.current_answers)+1, quiz)
    
    def sumbit_answer(self, answer) -> None:
        if self.quizzes[len(self.current_answers)]["answer"] == answer:
            self.current_answers.append((answer, True))
        else:
            self.current_answers.append((answer, False))

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