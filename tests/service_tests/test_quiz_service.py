import unittest
from unittest.mock import MagicMock, call
from services.quiz_service import QuizService, Badge, QuizType

class TestQuizService(unittest.TestCase):
    def setUp(self):
        # Mock the DataService dependency
        self.data_service_mock = MagicMock()

        # Create a QuizService instance with mocked dependency
        self.quiz_service = QuizService(self.data_service_mock)

    def test_configure(self):
        # Arrange
        new_config = {
            'num_questions': 20,
            'difficulty_range': (5, 15),
            'categories': ['category1', 'category2'],
            'all_categories': False,
            'is_timed': True,
            'max_time': 10
        }

        # Act
        self.quiz_service.configure(new_config)

        # Assert
        self.assertEqual(self.quiz_service.config, new_config)
        self.assertEqual(self.quiz_service.type, QuizType.CUSTOM)

    def test_configure_classic(self):
        # Act
        self.quiz_service.configure_classic()

        # Assert
        expected_config = {
            'num_questions': 10,
            'difficulty_range': (1, 10),
            'categories': [],
            'all_categories': True,
            'is_timed': False,
            'max_time': 5
        }
        self.assertEqual(self.quiz_service.type, QuizType.CLASSIC)
        self.assertEqual(self.quiz_service.config, expected_config)

    def test_configure_timed(self):
        # Act
        self.quiz_service.configure_timed()

        # Assert
        expected_config = {
            'num_questions': 10,
            'difficulty_range': (1, 10),
            'categories': [],
            'all_categories': True,
            'is_timed': True,
            'max_time': 5
        }
        self.assertEqual(self.quiz_service.type, QuizType.TIMED)
        self.assertEqual(self.quiz_service.config, expected_config)

    def test_configure_improvement(self):
        # Arrange
        self.data_service_mock.get_user_improvements.return_value = [('category1', '-10'), ('category2', '-10')]

        # Act
        self.quiz_service.configure_improvement()

        # Assert
        expected_config = {
            'num_questions': 10,
            'difficulty_range': (1, 10),
            'categories': ['category1', 'category2'],
            'all_categories': False,
            'is_timed': False,
            'max_time': 5,
        }
        self.assertEqual(self.quiz_service.type, QuizType.IMPROVEMENT)
        self.assertEqual(self.quiz_service.config, expected_config)

    def test_generate_quiz_no_categories(self):
        # Arrange
        self.quiz_service.config = {'all_categories': False, 'categories': []}

        # Act
        result = self.quiz_service.generate_quiz()

        # Assert
        self.assertFalse(result)

    def test_generate_quiz_with_categories(self):
        # Arrange
        self.quiz_service.config = {'num_questions': 2, 'all_categories': False, 'categories': ['category1', 'category2'], 'difficulty_range': (1, 10),}
        self.data_service_mock.get_quiz_bank.return_value = {"questions": [
            {"category": "category1", "difficulty": 5},
            {"category": "category2", "difficulty": 8},
            {"category": "category3", "difficulty": 3}
        ]}

        # Act
        result = self.quiz_service.generate_quiz()

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.quiz_service.quizzes), 2)  # Ensure correct number of questions selected

    def test_get_time(self):
        # Arrange
        self.quiz_service.config = {'is_timed': True, 'max_time': 10}

        # Act
        result = self.quiz_service.get_time()

        # Assert
        self.assertEqual(result, (True, 10))

    def test_get_quizzes_size(self):
        # Arrange
        self.quiz_service.quizzes = [1, 2, 3]

        # Act
        result = self.quiz_service.get_quizzes_size()

        # Assert
        self.assertEqual(result, 3)

    def test_get_quiz(self):
        # Arrange
        self.quiz_service.quizzes = [
            {"question": "Q1", "answer": "A1", "difficulty": 5, "category": "category1"},
            {"question": "Q2", "answer": "A2", "difficulty": 8, "category": "category2"},
            {"question": "Q3", "answer": "A3", "difficulty": 3, "category": "category1"}
        ]
        self.quiz_service.current_answers = [("", False)] * 3

        # Act
        result = self.quiz_service.get_quiz(1)

        # Assert
        self.assertEqual(result[0], 1)  # Ensure correct quiz number
        self.assertIn(result[1]["question"], "Q1")  # Ensure correct question selected

    def test_get_quiz_final(self):
        # Arrange
        self.quiz_service.quizzes = [
            {"question": "Q1", "answer": "A1", "difficulty": 5, "category": "category1"},
            {"question": "Q2", "answer": "A2", "difficulty": 8, "category": "category2"}
        ]
        self.quiz_service.current_answers = [("", False)] * 2
        self.quiz_service.at = 1

        # Act
        result = self.quiz_service.get_quiz(1)

        # Assert
        self.assertEqual(result, ())  # Ensure empty tuple returned

    def test_submit_answer_correct(self):
        # Arrange
        self.quiz_service.quizzes = [{"answer": "Answer 1"}, {"answer": "Answer 2"}]
        self.quiz_service.current_answers = [("", False)] * 2
        self.quiz_service.at = 0

        # Act
        self.quiz_service.submit_answer("Answer 1")

        # Assert
        self.assertEqual(self.quiz_service.current_answers[self.quiz_service.at], ("Answer 1", True))

    def test_submit_answer_incorrect(self):
        # Arrange
        self.quiz_service.quizzes = [{"answer": "Answer 1"}, {"answer": "Answer 2"}]
        self.quiz_service.current_answers = [("", True)] * 2
        self.quiz_service.at = 0

        # Act
        self.quiz_service.submit_answer("Incorrect Answer")

        # Assert
        self.assertEqual(self.quiz_service.current_answers[self.quiz_service.at], ("Incorrect Answer", False))

    def test_terminate_quiz(self):
        # Act
        self.quiz_service.terminate_quiz()

        # Assert
        self.assertTrue(self.quiz_service.time >= 0)

    def test_quiz_timeout(self):
        # Arrange
        self.quiz_service.quizzes = [{"category": "category_1", "difficulty": "1"}, {"category": "category_2", "difficulty": "2"}]

        # Act
        self.quiz_service.quiz_timeout()

        # Assert
        self.assertTrue(self.quiz_service.time >= 0)
        self.assertEqual(self.quiz_service.average_difficulty, 3.0)  # Sum of difficulties for both questions
        self.assertEqual(len(self.quiz_service.category_quiz), 2)

    def test_check_answers(self):
        # Arrange
        self.quiz_service.current_answers = [("", False)] * 2

        # Act
        result = self.quiz_service.check_answers()

        # Assert
        self.assertEqual(result, (0, 2))  # One correct answer out of two questions
        self.data_service_mock.update_user_quiz.assert_called_once_with(0)  # Check if update_user_quiz is called with the correct number of correct answers

    def test_quiz_badge(self):
        # Arrange
        self.quiz_service.current_answers = [("", True)] * 20
        self.quiz_service.quizzes = [{"category": "category_1"}] * 20
        self.quiz_service.type = QuizType.IMPROVEMENT

        # Act
        result = self.quiz_service.check_answers()

        # Assert
        self.assertEqual(result, (20, 20))  # One correct answer out of two questions
        calls = [call(Badge.QUIZ_WHIZ), call(Badge.LEARNER)]
        self.data_service_mock.update_user_badge.assert_has_calls(calls)
        self.assertEqual(self.data_service_mock.update_user_badge.call_count, 2)

    def test_check_difficulty(self):
        # Arrange
        self.quiz_service.quizzes = [{}] * 5
        self.quiz_service.average_difficulty = 11
        
        # Act
        result = self.quiz_service.check_difficulty()

        # Assert
        self.assertEqual(result, 2.2)

    def test_check_time(self):
        # Arrange
        self.quiz_service.time = 125

        # Act
        result = self.quiz_service.check_time()

        # Assert
        self.assertEqual(result, "02:05")  # Time formatted as MM:SS

    def test_check_time_per_question(self):
        # Arrange
        self.quiz_service.time = 125
        self.quiz_service.quizzes = [{}] * 5

        # Act
        result = self.quiz_service.check_time_per_question()

        # Assert
        self.assertEqual(result, "00:25")  # Time per question formatted as MM:SS

    def test_get_all_categories(self):
        # Mock data_service.get_quiz_bank() to return categories
        self.data_service_mock.get_quiz_bank.return_value = {"categories": ["Category 1", "Category 2", "Category 3"]}

        # Act
        result = self.quiz_service.get_all_categories()

        # Assert
        self.assertEqual(result, ["Category 1", "Category 2", "Category 3"])

    def test_category_analyse(self):
        # Arrange
        self.quiz_service.category_quiz = {"c1": 10, "c2": 10, "c3": 10}
        self.quiz_service.category_answer = {"c1": 5, "c2": 10, "c3": 7}
        
        # Act
        result = self.quiz_service.category_analyse()

        # Assert
        self.assertEqual(len(result), 3)  # Two categories analyzed
        self.assertEqual(result[0][0], "c1")  # Category with the lowest percentage
        self.assertEqual(result[2][0], "c2")  # Category with the highest percentage
        self.data_service_mock.update_user_improvement.assert_called_once_with([("c1", 0), ("c2", 10), ("c3", 4)])  # Check if update_user_improvement is called with correct data


