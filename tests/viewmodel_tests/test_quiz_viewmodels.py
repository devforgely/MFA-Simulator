import unittest
from unittest.mock import MagicMock, patch
from viewmodels.quiz_viewmodels import QuizViewModel, QuizSettingsViewModel, QuizPlayViewModel, QuizResponseViewModel

class TestQuizViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock):
        self.view_model = QuizViewModel()

    def test_on_message_play_quiz(self):
        # Mocking change signal
        self.view_model.view_quiz = MagicMock()

        # Emitting the "Play Quiz" message
        self.view_model.on_message("Play Quiz")

        # Asserting if the view_quiz signal is emitted
        self.view_model.view_quiz.emit.assert_called_once()

    def test_on_message_quiz_response(self):
        # Mocking change signal
        self.view_model.view_response = MagicMock()

        # Emitting the "Quiz Response" message
        self.view_model.on_message("Quiz Response")

        # Asserting if the view_response signal is emitted
        self.view_model.view_response.emit.assert_called_once()

    def test_on_message_quiz_settings(self):
        # Mocking change signal
        self.view_model.view_setting = MagicMock()

        # Emitting the "Quiz Settings" message
        self.view_model.on_message("Quiz Settings")

        # Asserting if the view_setting signal is emitted
        self.view_model.view_setting.emit.assert_called_once()


class TestQuizSettingsViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.data_service')
    @patch('services.container.ApplicationContainer.quiz_service')
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock, quiz_service_mock, data_service_mock):
        self.view_model = QuizSettingsViewModel()

    def test_on_message_update_quiz_expand(self):
        # Mocking change signal
        self.view_model.custom_setting_expand_changed = MagicMock()

        # Emitting the "Update Custom Quiz" message
        self.view_model.on_message("Update Custom Quiz", True)

        # Asserting if the view_quiz signal is emitted
        self.view_model.custom_setting_expand_changed.emit.assert_called_once_with(True)

    def test_custom_setting_expand(self):
        # Mocking change signal
        self.view_model.custom_setting_expand_changed = MagicMock()

        # Calling the custom_setting_expand method
        self.view_model.custom_setting_expand()

        # Asserting if the custom_setting_expand_changed signal is emitted with the correct value
        self.view_model.custom_setting_expand_changed.emit.assert_called_once_with(self.view_model.data_service.get_custom_quiz_setting_expand())

    def test_quiz_categories(self):
        # Mocking change signal
        self.view_model.category_list_changed = MagicMock()

        # Calling the quiz_categories method
        self.view_model.quiz_categories()

        # Asserting if the category_list_changed signal is emitted with the correct value
        self.view_model.category_list_changed.emit.assert_called_once_with(self.view_model.quiz_service.get_all_categories())

    def test_set_classic(self):
        # Mocking configure_classic method
        self.view_model.quiz_service.configure_classic = MagicMock()

        # Calling the set_classic method
        self.view_model.set_classic()

        # Asserting if the configure_classic method is called
        self.view_model.quiz_service.configure_classic.assert_called_once()

    def test_set_timed(self):
        # Mocking configure_timed method
        self.view_model.quiz_service.configure_timed = MagicMock()

        # Calling the set_timed method
        self.view_model.set_timed()

        # Asserting if the configure_timed method is called
        self.view_model.quiz_service.configure_timed.assert_called_once()

    def test_set_improvement(self):
        # Mocking configure_improvement method
        self.view_model.quiz_service.configure_improvement = MagicMock()

        # Calling the set_improvement method
        self.view_model.set_improvement()

        # Asserting if the configure_improvement method is called
        self.view_model.quiz_service.configure_improvement.assert_called_once()

    def test_is_text_in_list(self):
        # Adding a category to the list
        self.view_model.list_categories.append("Category1")

        # Testing if the category is in the list
        self.assertTrue(self.view_model.is_text_in_list("Category1"))

        # Testing if a non-existing category is not in the list
        self.assertFalse(self.view_model.is_text_in_list("Category2"))

    def test_append_category(self):
        # Calling the append_category method
        self.view_model.append_category("Category1")

        # Asserting if the category is appended to the list
        self.assertIn("Category1", self.view_model.list_categories)

    def test_remove_category(self):
        # Adding a category to the list
        self.view_model.list_categories.append("Category1")

        # Calling the remove_category method
        self.view_model.remove_category("Category1")

        # Asserting if the category is removed from the list
        self.assertNotIn("Category1", self.view_model.list_categories)

    def test_validate_quiz_setting_valid(self):
        # Calling the validate_quiz_setting method with valid parameters
        result = self.view_model.validate_quiz_setting("1-5", "10", False, False, "5")

        # Asserting that the method returns True
        self.assertTrue(result)

    def test_validate_quiz_setting_invalid(self):
        # Calling the validate_quiz_setting method with invalid parameters
        result = self.view_model.validate_quiz_setting("5-1", "10", False, False, "5")

        # Asserting that the method returns False
        self.assertFalse(result)

    def test_validate_quiz_setting_invalid_2(self):
        # Calling the validate_quiz_setting method with invalid parameters
        result = self.view_model.validate_quiz_setting("92", "10", False, False, "5")

        # Asserting that the method returns False
        self.assertFalse(result)

    def test_validate_quiz_setting_invalid_3(self):
        # Calling the validate_quiz_setting method with invalid parameters
        result = self.view_model.validate_quiz_setting("1-3", "0", False, False, "5")

        # Asserting that the method returns False
        self.assertFalse(result)

    def test_prepare_quiz_success(self):
        # Mocking generate_quiz method
        self.view_model.quiz_service.generate_quiz.return_value = True

        # Mocking message service send method
        self.view_model.message_service.send = MagicMock()

        # Calling the prepare_quiz method
        result = self.view_model.prepare_quiz()

        # Asserting if the message service send method is called with the correct parameters
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Play Quiz")
        
        # Asserting that the method returns True
        self.assertTrue(result)

    def test_prepare_quiz_failure(self):
        # Mocking generate_quiz method
        self.view_model.quiz_service.generate_quiz.return_value = False

        # Mocking message service send method
        self.view_model.message_service.send = MagicMock()

        # Calling the prepare_quiz method
        result = self.view_model.prepare_quiz()

        # Asserting that the message service send method is not called
        self.assertFalse(self.view_model.message_service.send.called)
        
        # Asserting that the method returns False
        self.assertFalse(result)


class TestQuizPlayViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.quiz_service')
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock, quiz_service_mock):
        quiz_service_mock.return_value.get_quizzes_size.return_value = 5
        quiz_service_mock.return_value.get_time.return_value = (False, 5)
        quiz_service_mock.return_value.get_quiz.return_value = ({"question": "Question 1 name", "choices": ["A1", "A2"], "answer": "A1", "difficulty": 5, "category": "category1"}, 1)

        self.view_model = QuizPlayViewModel()

    def test_on_message_play_quiz_not_timed(self):
        self.view_model.on_message("Play Quiz")

        # Asserting quiz service methods are called correctly
        self.view_model.quiz_service.get_quizzes_size.assert_called_once()
        self.view_model.quiz_service.get_time.assert_called_once()
        self.view_model.quiz_service.get_quiz.assert_called_once_with(1)

        self.assertEqual(self.view_model.max_time, 0)
        self.assertEqual(self.view_model.quiz_size, 5)
        self.assertEqual(self.view_model.saved_choice, "")
        self.assertFalse(hasattr(self.view_model, 'threading'))

    @patch('widgets.timer.TimeDisplayThread.start')
    def test_on_message_play_quiz_timed(self, mock_thread_start):
        self.view_model.quiz_service.get_time.return_value = (True, 5)
        self.view_model.on_message("Play Quiz")

        # Asserting quiz service methods are called correctly
        self.view_model.quiz_service.get_quizzes_size.assert_called_once()
        self.view_model.quiz_service.get_time.assert_called_once()
        self.view_model.quiz_service.get_quiz.assert_called_once_with(1)

        self.assertEqual(self.view_model.max_time, 300)
        self.assertEqual(self.view_model.yellow_time, 150)
        self.assertEqual(self.view_model.red_time, 60)
        self.assertEqual(self.view_model.quiz_size, 5)
        self.assertEqual(self.view_model.saved_choice, "")
        self.assertTrue(hasattr(self.view_model, 'threading'))
        mock_thread_start.assert_called_once()

    def test_signal_update(self):
        # Mocking signal
        self.view_model.time_color_changed = MagicMock()

        # Test when val equals yellow_time
        self.view_model.yellow_time = 10
        self.view_model.signal_update(10, 0, 10)
        self.view_model.time_color_changed.emit.assert_called_once_with("#ffcd27")

        # Test when val equals red_time
        self.view_model.red_time = 5
        self.view_model.signal_update(5, 0, 5)
        self.view_model.time_color_changed.emit.assert_called_with("#f44336")

        # Test when val is not yellow_time or red_time
        self.view_model.time_color_changed.reset_mock()
        self.view_model.signal_update(90, 1, 30)
        self.assertFalse(self.view_model.time_color_changed.emit.called)

        # Test when val equals 0
        self.view_model.signal_update(0, 0, 0)
        self.view_model.quiz_service.quiz_timeout.assert_called_once()
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Quiz Response")

    def test_save_choice(self):
        self.view_model.save_choice("A1")
        self.assertEqual(self.view_model.saved_choice, "A1")

    def test_next_quiz(self):
        # Mocking signal
        self.view_model.quiz_changed = MagicMock()

        # Mock quiz_service.get_quiz to return a quiz for the next call
        self.view_model.quiz_service.get_quiz.return_value = ({"question": "Question 2", "choices": ["B1", "B2"], "answer": "B1"}, 1)

        # viewmodel default
        self.view_model.quiz_size = 3
        self.view_model.max_time = 120
        self.view_model.saved_choice = "A1"

        # Call next_quiz
        self.view_model.next_quiz()

        # Check if quiz_changed signal is emitted with the correct quiz and size
        self.view_model.quiz_changed.emit.assert_called_once_with(({"question": "Question 2", "choices": ["B1", "B2"], "answer": "B1"}, 1), 3)

        # Check if saved_choice is reset
        self.assertEqual(self.view_model.saved_choice, "")

        # Test when there are no more quizzes
        self.view_model.threading = MagicMock()
        self.view_model.quiz_service.get_quiz.return_value = ()
        self.view_model.next_quiz()

        # Check if threading stop method is called
        self.view_model.threading.stop.assert_called_once()
        # Check if Quiz Response message is sent
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Quiz Response")

    def test_quiz_before(self):
        # Mocking signal
        self.view_model.quiz_changed = MagicMock()

        # Mock quiz_service.get_quiz to return a quiz for the previous call
        self.view_model.quiz_service.get_quiz.return_value = ({"question": "Question 0", "choices": ["A0", "A1"], "answer": "A0"}, 1)

        # Call quiz_before
        self.view_model.quiz_before()

        # Check if quiz_changed signal is emitted with the correct quiz and size
        self.view_model.quiz_changed.emit.assert_called_once_with(({"question": "Question 0", "choices": ["A0", "A1"], "answer": "A0"}, 1), 0)


class TestQuizResponseViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.quiz_service')
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock, quiz_service_mock):
        self.view_model = QuizResponseViewModel()

    def test_on_message_quiz_response(self):
        # Mocking signals
        self.view_model.check_time_changed = MagicMock()
        self.view_model.time_per_question_changed = MagicMock()
        self.view_model.difficulty_changed = MagicMock()
        self.view_model.score_changed = MagicMock()
        self.view_model.quiz_detail_changed = MagicMock()

        # Mock return values for quiz_service methods
        self.view_model.quiz_service.get_time.return_value = (True, 5)
        self.view_model.quiz_service.check_time.return_value = "03:45"
        self.view_model.quiz_service.check_time_per_question.return_value = "00:20"
        self.view_model.quiz_service.check_difficulty.return_value = 3.1
        self.view_model.quiz_service.check_answers.return_value = (8, 10)
        self.view_model.quiz_service.quizzes = []
        self.view_model.quiz_service.current_answers = []
        self.view_model.quiz_service.category_analyse.return_value = [("c1", 0), ("c2", 10), ("c3", 4)]

        # Call on_message with "Quiz Response" message title
        self.view_model.on_message("Quiz Response")

        # Assert that signals are emitted with the correct arguments
        self.view_model.check_time_changed.emit.assert_called_once_with(True, 5, "03:45")
        self.view_model.time_per_question_changed.emit.assert_called_once_with("00:20")
        self.view_model.difficulty_changed.emit.assert_called_once_with("3.1")
        self.view_model.score_changed.emit.assert_called_once_with(8, 10)
        self.view_model.quiz_detail_changed.emit.assert_called_once_with(self.view_model.quiz_service.quizzes, self.view_model.quiz_service.current_answers, [("c1", 0), ("c2", 10), ("c3", 4)])

    def test_back(self):
        # Call the back method
        self.view_model.back()

        # Assert that the message_service send method is called with the correct parameters
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Quiz Settings") 