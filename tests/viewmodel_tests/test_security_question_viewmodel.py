import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.security_question_viewmodel import SecurityQuestionRegisterViewModel, SecurityQuestionAuthenticateViewModel

class TestPicturePasswordRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.data_service")
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service, mock_data_service):
        self.viewmodel = SecurityQuestionRegisterViewModel()

    def test_add_question(self):
        # Case: Maximum questions not reached
        self.viewmodel.question_size = 3
        self.viewmodel.add_question_signal = MagicMock()
        self.viewmodel.add_question()
        self.viewmodel.add_question_signal.emit.assert_called()
        self.assertEqual(self.viewmodel.question_size, 4)

        # Case: Maximum questions reached
        self.viewmodel.question_size = 5
        self.viewmodel.add_question_signal = MagicMock()
        self.viewmodel.add_question()
        self.viewmodel.add_question_signal.emit.assert_not_called()
        self.assertEqual(self.viewmodel.question_size, 5)

    def test_remove_question(self):
        # Case: Minimum questions not reached
        self.viewmodel.question_size = 3
        self.viewmodel.remove_question_signal = MagicMock()
        self.viewmodel.remove_question()
        self.viewmodel.remove_question_signal.emit.assert_called()
        self.assertEqual(self.viewmodel.question_size, 2)

        # Case: Minimum questions reached
        self.viewmodel.question_size = 2
        self.viewmodel.remove_question_signal = MagicMock()
        self.viewmodel.remove_question()
        self.viewmodel.remove_question_signal.emit.assert_not_called()
        self.assertEqual(self.viewmodel.question_size, 2)

    def test_recover_unselected_question(self):
        # Case: Recover unselected question
        question = "What is your favorite color?"
        self.viewmodel.unselected_question = []
        self.viewmodel.unselected_changed = MagicMock()
        self.viewmodel.recover_unselected_question(question)
        self.assertEqual(len(self.viewmodel.unselected_question), 1)
        self.assertIn(question, self.viewmodel.unselected_question)
        self.viewmodel.unselected_changed.emit.assert_called_once_with(self.viewmodel.unselected_question)

    def test_on_question_selected(self):
        # Case: On question selected
        question = "What is your favorite color?"
        self.viewmodel.unselected_question = [question]
        self.viewmodel.unselected_changed = MagicMock()
        self.viewmodel.on_question_selected(question)
        self.assertEqual(len(self.viewmodel.unselected_question), 0)
        self.assertNotIn(question, self.viewmodel.unselected_question)
        self.viewmodel.unselected_changed.emit.assert_called_once_with(self.viewmodel.unselected_question)

    def test_add_security_answer(self):
        # Case: Add security answer
        question = "What is your favorite color?"
        answer = "Blue"
        self.viewmodel.add_security_answer(question, answer)
        self.assertEqual(len(self.viewmodel.questions), 1)
        self.assertIn(question, self.viewmodel.questions)
        self.assertEqual(self.viewmodel.answer_key, "blue$")

    def test_clear_security_answer(self):
        # Case: Clear security answer
        self.viewmodel.questions = ["What is your favorite color?", "What is your pet's name?"]
        self.viewmodel.answer_key = "blue$dog$"
        self.viewmodel.clear_security_answer()
        self.assertEqual(len(self.viewmodel.questions), 0)
        self.assertEqual(self.viewmodel.answer_key, "")

    def test_state_data(self):
        mock_data = {
            "user_questions": ["question1", "question2"],
            "hashed_secret": b"secret",
            "salt": b"salt"
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["user_questions"], str))
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertTrue(isinstance(result["salt"], str))

    @patch.object(SecurityQuestionRegisterViewModel, "clear_security_answer")
    @patch("viewmodels.authentication.security_question_viewmodel.normalise_text")
    def test_send(self, mock_normalise_text, mock_clear_question):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}
       
        # Case: Too short answer
        self.viewmodel.too_short_flag = True
        self.viewmodel.send()
        self.assertEqual(self.viewmodel.too_short_flag, False)
        mock_clear_question.assert_called_once()
        self.viewmodel.state_change.emit.assert_called_with("Your answer must be at least three characters long and case-sensitive is ignored.", 1)

        # Case: Registration successful
        self.viewmodel.too_short_flag = False
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Account has been registered.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.too_short_flag = False
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)


class TestPicturePasswordAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = SecurityQuestionAuthenticateViewModel()

    def test_questions_stored(self):
        # Case: Questions stored
        self.viewmodel.authentication_service.get_session_stored.return_value = {"user_questions": ["Question 1", "Question 2"]}
        result = self.viewmodel.questions_stored()
        self.assertEqual(result, ["Question 1", "Question 2"])

    def test_state_data(self):
        mock_data = {
            "user_questions": ["question1", "question2"],
            "hashed_secret": b"secret",
            "salt": b"salt"
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["user_questions"], str))
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertTrue(isinstance(result["salt"], str))

    def test_add_answer(self):
        # Case: Add answer
        self.viewmodel.answer_key = ""
        self.viewmodel.answer_size = 0
        self.viewmodel.add_answer("blue")
        self.viewmodel.add_answer("life")
        self.assertEqual(self.viewmodel.answer_key, "blue$life$")
        self.assertEqual(self.viewmodel.answer_size, 2)

    def test_send(self):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_once_with("The user has been authenticated.", 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(), 0)
        self.assertEqual(self.viewmodel.answer_key, "")
        self.assertEqual(self.viewmodel.answer_size, 0)

        # Case: Incorrect credentials
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_once_with("These credentials does not match our records.", 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(), 2)

    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.bypass()
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)

    