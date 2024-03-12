import unittest
from unittest.mock import MagicMock, patch
from services.data_service import DataService, Settings, User, UserPreference, Note, Badge
from services.message_service import MessageService
import json


class TestDataServices(unittest.TestCase):
    def setUp(self):
        # Mock the MessageService instance
        self.message_service_mock = MagicMock(spec=MessageService)

    @patch.object(DataService, 'read_notes_titles')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_initialization_file_exist(self, mock_path_exists, mock_open, mock_read_notes_titles):
        # Arrange
        mock_path_exists.return_value = True
        data = {"user": {"coins": 700, "quiz_completed": 5, "simulation_played": 12, "recent_activities": [["Quiz Completion", "Saturday, Mar 09, 2024, 03:45 PM", "Great job on completing the quiz! Keep learning."], ["Quiz Completion", "Saturday, Mar 09, 2024, 03:46 PM", "Great job on completing the quiz! Keep learning."], ["Quiz Completion", "Saturday, Mar 09, 2024, 05:24 PM", "Great job on completing the quiz! Keep learning."]], "badges": [[0, "b5.png"], [1, "b6.png"], [6, "b3.png"]], "improvements": [["MFA concepts", -6], ["MFA challenges", -3], ["MFA technologies", -6], ["RSA concepts", -2]], "readings": [["A Reading List", 2], ["Biometric", 2], ["Chip & Pin", 2], ["Cryptographic Device", False], ["Memorised Secret", 2], ["Picture Password", 2], ["TOTP", False]], "unlocked_simulations": {"1": True, "2": True, "3": True, "4": True, "5": True, "6": True, "7": True}}, "user_preference": {"start_up_index": 0, "custom_quiz_setting_expand": False, "show_notification": True}}
        mock_file_content = json.dumps(data)
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        mock_read_notes_titles.return_value = [Note("test", ""), Note("test2", "")]

        # Act
        data_service = DataService(self.message_service_mock)

        # Assert
        self.assertEqual(data_service.message_service, self.message_service_mock)
        self.assertEqual(data_service.user_path, Settings.USER_FILE_PATH)
        mock_open.assert_called_once_with(Settings.USER_FILE_PATH, 'r')
        self.assertFalse(data_service.signal_update)

        mock_read_notes_titles.assert_called_once()
        self.assertEqual(len(data_service.notes), 2)
        self.assertEqual(data_service.notes[1].title, "test2")
 
        self.assertEqual(data_service.user.coins, 700)
        self.assertEqual(data_service.user.quiz_completed, 5)
        self.assertEqual(data_service.user.simulation_played, 12)
        self.assertEqual(data_service.user_preference.start_up_index, 0)
        self.assertEqual(data_service.user_preference.custom_quiz_setting_expand, False)

        self.assertEqual(data_service.cached_quiz_bank, [])
        self.assertEqual(data_service.cached_security_questions, [])
        self.assertEqual(data_service.cached_facts, [])
        self.assertEqual(data_service.cached_details, {})
        self.assertEqual(data_service.cache_help_index, dict())


    @patch.object(DataService, 'read_notes_titles')
    @patch.object(DataService, 'reset_data')
    @patch('os.path.exists')
    def test_initialization_file_not_exists(self, mock_path_exists, mock_reset_data, mock_read_notes_titles):
        # Arrange
        mock_path_exists.return_value = False
        mock_read_notes_titles.return_value = [Note("test", ""), Note("test2", "")]

        # Act
        data_service = DataService(self.message_service_mock)

        # Assert
        mock_reset_data.assert_called_once()
        self.assertFalse(data_service.signal_update)
    
    @patch.object(DataService, 'read_notes_titles')
    @patch('json.dump')
    @patch('builtins.open')
    def test_save_data_update(self, mock_open, mock_dump, mock_read_notes_titles):
        # Arrange
        data_service = DataService(self.message_service_mock)
        data_service.signal_update = True

        mock_open.reset_mock()
        mock_dump.reset_mock()

        # Act
        data_service.save_data()

        # Assert
        mock_open.assert_called_once_with(Settings.USER_FILE_PATH, 'w')
        mock_dump.assert_called_once()
        self.assertFalse(data_service.signal_update)

    @patch.object(DataService, 'read_notes_titles')
    @patch('json.dump')
    @patch('builtins.open')
    def test_save_data_not_update(self, mock_open, mock_dump, mock_read_notes_titles):
        # Arrange
        data_service = DataService(self.message_service_mock)
        data_service.signal_update = False

        mock_open.reset_mock()
        mock_dump.reset_mock()

        # Act
        data_service.save_data()

        # Assert
        mock_open.assert_not_called()
        mock_dump.assert_not_called()
        self.assertFalse(data_service.signal_update)


    @patch.object(DataService, 'read_notes_titles')
    @patch('json.dump')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_reset_data(self, mock_path_exists, mock_open, mock_dump, mock_read_notes_titles):
        # Arrange
        mock_path_exists.return_value = True
        data = {"user": {"coins": 700, "quiz_completed": 5, "simulation_played": 12, "recent_activities": [["Quiz Completion", "Saturday, Mar 09, 2024, 03:45 PM", "Great job on completing the quiz! Keep learning."], ["Quiz Completion", "Saturday, Mar 09, 2024, 03:46 PM", "Great job on completing the quiz! Keep learning."], ["Quiz Completion", "Saturday, Mar 09, 2024, 05:24 PM", "Great job on completing the quiz! Keep learning."]], "badges": [[0, "b5.png"], [1, "b6.png"], [6, "b3.png"]], "improvements": [["MFA concepts", -6], ["MFA challenges", -3], ["MFA technologies", -6], ["RSA concepts", -2]], "readings": [["A Reading List", 2], ["Biometric", 2], ["Chip & Pin", 2], ["Cryptographic Device", False], ["Memorised Secret", 2], ["Picture Password", 2], ["TOTP", False]], "unlocked_simulations": {"1": True, "2": True, "3": True, "4": True, "5": True, "6": True, "7": True}}, "user_preference": {"start_up_index": 0, "custom_quiz_setting_expand": False, "show_notification": True}}
        mock_file_content = json.dumps(data)
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        data_service = DataService(self.message_service_mock)
        data_service.signal_update = True

        mock_open.reset_mock()
        mock_dump.reset_mock()

        # Act
        data_service.reset_data()

        # Assert
        mock_open.assert_called_once_with(Settings.USER_FILE_PATH, 'w')
        # Check if the user and user_preference attributes are reset
        self.assertIsInstance(data_service.user, User)
        self.assertIsInstance(data_service.user_preference, UserPreference)
        self.assertEqual(data_service.user.coins, 100)
        self.assertEqual(data_service.user.quiz_completed, 0)
        self.assertEqual(data_service.user.simulation_played, 0)
        self.assertEqual(data_service.user_preference.start_up_index, 0)
        self.assertEqual(data_service.user_preference.custom_quiz_setting_expand, False)
        self.assertFalse(data_service.signal_update)
        self.message_service_mock.send.assert_called_once_with(data_service, "Reboot")


class TestDataServiceUser(unittest.TestCase):
    @patch.object(DataService, 'read_notes_titles')
    @patch('builtins.open')
    @patch('os.path.exists')
    def setUp(self, mock_path_exists, mock_open, mock_read_notes_titles):
        # Mock the MessageService instance
        self.message_service_mock = MagicMock(spec=MessageService)

        mock_path_exists.return_value = True
        data = {"user": {"coins": 400, "quiz_completed": 0, "simulation_played": 0, "recent_activities": [], "badges": [], "improvements": [], "readings": [["title1", False], ["title2", False]], "unlocked_simulations": {"1": True, "2": False, "3": False, "4": False, "5": False, "6": False, "7": False}}, "user_preference": {"start_up_index": 0, "custom_quiz_setting_expand": False, "show_notification": True}}
        mock_file_content = json.dumps(data)
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        mock_read_notes_titles.return_value = []
        # Create a DataService instance
        self.data_service = DataService(self.message_service_mock)

    def test_update_user_coin_badge(self):
        # Arrange
        value = 600

        # Act
        result = self.data_service.update_user_coin(value)

        # Assert
        self.assertTrue(result)  # Check that the method returns True
        self.assertEqual(self.data_service.user.coins, 1000)  # Check that coins are updated correctly
        self.assertTrue(Badge.COIN_HUNTER.value in self.data_service.user.badges)
        self.assertTrue(self.data_service.signal_update)
        self.assertEqual(self.message_service_mock.send.call_count, 2)

    def test_update_user_coin_sufficient_coins(self):
        # Arrange
        value = -300  # Deduct 300 coins

        # Act
        result = self.data_service.update_user_coin(value)

        # Assert
        self.assertTrue(result)  # Check that the method returns True
        self.assertEqual(self.data_service.user.coins, 100)  # Check that coins are updated correctly
        self.assertTrue(self.data_service.signal_update)
        self.message_service_mock.send.assert_called_once()

    def test_update_user_coin_insufficient_coins(self):
        # Arrange
        value = -1000  # Deduct 1000 coins

        # Act
        result = self.data_service.update_user_coin(value)

        # Assert
        self.assertFalse(result)  # Check that the method returns False
        self.assertEqual(self.data_service.user.coins, 400)  # Check that coins remain unchanged
        self.assertFalse(self.data_service.signal_update)
        self.message_service_mock.send.assert_called_once()

    @patch.object(User, 'add_activity')
    def test_update_user_quiz(self, mock_add_activity):
        # Act
        self.data_service.update_user_quiz(correct=3)

        # Assert
        self.assertEqual(self.data_service.user.quiz_completed, 1)  # Check that quiz completion count is incremented
        self.assertEqual(self.data_service.user.coins, 400 + 3 * 20)  # Check that coins are updated correctly
        mock_add_activity.assert_called_once()
        self.assertTrue(self.data_service.signal_update)
        self.assertEqual(self.message_service_mock.send.call_count, 2)

    
    @patch.object(User, 'add_activity')
    def test_update_user_simulation(self, mock_add_activity):
        # Act
        self.data_service.update_user_simulation()

        # Assert
        self.assertEqual(self.data_service.user.simulation_played, 1)  # Check that simulation played count is incremented
        self.assertEqual(self.data_service.user.coins, 400 + 100)  # Check that coins are updated correctly
        mock_add_activity.assert_called_once()
        self.assertTrue(self.data_service.signal_update)
        self.assertEqual(self.message_service_mock.send.call_count, 2)

    def test_update_user_badge(self):
        # Act
        self.data_service.update_user_badge(Badge.ONE_FA)

        # Assert
        self.assertTrue(Badge.ONE_FA.value in self.data_service.user.badges)
        self.assertTrue(self.data_service.signal_update)
        self.message_service_mock.send.assert_called_once()

    def test_update_user_badge_no_update(self):
        # Arrange
        self.data_service.update_user_badge(Badge.ONE_FA)
        self.message_service_mock.reset_mock()
        self.data_service.signal_update = False

        # Act
        self.data_service.update_user_badge(Badge.ONE_FA)

        # Assert
        self.assertFalse(self.data_service.signal_update)
        self.message_service_mock.send.assert_not_called()

    def test_update_user_improvement(self):
        # Arrange
        improvements = [('improvement1', -10), ('improvement2', -20)]

        # Act
        self.data_service.update_user_improvement(improvements)

        # Assert
        self.assertEqual(len(self.data_service.user.improvements), 2)
        self.assertTrue(self.data_service.signal_update)
        self.message_service_mock.send.assert_called_once_with(self.data_service, "Update Improvements", None)
   
    @patch.object(DataService, 'update_user_badge')
    def test_update_user_reading(self, mock_update_badge):
        # Act
        self.data_service.update_user_reading('title1', True, 0)
        self.data_service.update_user_reading('title2', True, 1)

        # Assert
        self.assertTrue(self.data_service.signal_update)
        self.assertEqual(self.data_service.user.readings[0][1], True)
        self.assertEqual(self.data_service.user.readings[0][1], True)
        mock_update_badge.assert_called_once_with(Badge.SECURITY_SCHOLAR)

    @patch.object(User, 'unlock_simulation')
    def test_unlock_user_simulation(self, mock_unlock_simulation):
        # Act
        self.data_service.unlock_user_simulation(1)

        # Assert
        self.assertTrue(self.data_service.signal_update)
        mock_unlock_simulation.assert_called_once_with(1)

    def test_get_user_coins(self):
        # Act
        result = self.data_service.get_user_coins()

        # Assert
        self.assertEqual(result, 400)

    def test_get_user_simulation_played(self):
        # Act
        result = self.data_service.get_user_simulation_played()

        # Assert
        self.assertEqual(result, 0)

    def test_get_user_quiz_completed(self):
        # Act
        result = self.data_service.get_user_quiz_completed()

        # Assert
        self.assertEqual(result, 0)

    def test_get_user_recent_activiies(self):
        # Act
        result = self.data_service.get_user_recent_activiies()

        # Assert
        self.assertEqual(result, [])

    def test_get_user_badges(self):
        # Act
        result = self.data_service.get_user_badges()

        # Assert
        self.assertEqual(result, [])

    def test_get_user_badges_count(self):
        # Act
        result = self.data_service.get_user_badges_count()

        # Assert
        self.assertEqual(result, (0, 8))

    def test_get_user_improvements(self):
        # Act
        result = self.data_service.get_user_improvements()

        # Assert
        self.assertEqual(result, [])

    def test_get_user_readings(self):
        # Act
        result = self.data_service.get_user_readings()

        # Assert
        self.assertEqual(result, [["title1", False], ["title2", False]])

    def test_get_user_unlocked_simulations(self):
        # Act
        result = self.data_service.get_user_unlocked_simulations()

        # Assert
        self.assertEqual(result, {1: True, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False})


class TestDataServiceSystem(unittest.TestCase):
    @patch.object(DataService, 'read_notes_titles')
    @patch('builtins.open')
    @patch('os.path.exists')
    def setUp(self, mock_path_exists, mock_open, mock_read_notes_titles):
        # Mock the MessageService instance
        self.message_service_mock = MagicMock(spec=MessageService)

        mock_path_exists.return_value = True
        data =  data = {"user": {"coins": 400, "quiz_completed": 0, "simulation_played": 0, "recent_activities": [], "badges": [], "improvements": [], "readings": [["title1", False], ["title2", False]], "unlocked_simulations": {"1": True, "2": False, "3": False, "4": False, "5": False, "6": False, "7": False}}, "user_preference": {"start_up_index": 0, "custom_quiz_setting_expand": False, "show_notification": True}}
        mock_file_content = json.dumps(data)
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        mock_read_notes_titles.return_value = []
        # Create a DataService instance
        self.data_service = DataService(self.message_service_mock)

    def test_get_system_start_up(self):
        # Act
        result = self.data_service.get_system_start_up()

        # Assert
        self.assertEqual(result, 0)

    def test_change_system_start_up(self):
        # Act
        self.data_service.change_system_start_up(1)

        # Assert
        self.assertTrue(self.data_service.signal_update)
        self.assertEqual(self.data_service.user_preference.start_up_index, 1)

    def test_get_custom_quiz_setting_expand(self):
        # Act
        result = self.data_service.get_custom_quiz_setting_expand()

        # Assert
        self.assertFalse(result)

    def test_change_custom_quiz_setting_expand(self):
        # Act
        self.data_service.change_custom_quiz_setting_expand(True)

        # Assert
        self.assertTrue(self.data_service.signal_update)
        self.assertTrue(self.data_service.user_preference.custom_quiz_setting_expand)
        self.message_service_mock.send.assert_called_once_with(self.data_service, "Update Custom Quiz", True)

    def test_get_fun_fact_with_file_found(self):
        # Mock open function to simulate file existence
        with patch('builtins.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({"facts": ["Fact 1", "Fact 2"]})

            # Act
            result = self.data_service.get_fun_fact()

            # Assert
            self.assertEqual(len(self.data_service.cached_facts), 2)
            self.assertIn(result, ["Fact 1", "Fact 2"])

    def test_get_fun_fact_with_cache(self):
        # Arrange
        self.data_service.cached_facts = ["Fact 1", "Fact 2"]

        # Mock open function to simulate file existence
        with patch('builtins.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({"facts": ["Fact 4", "Fact 3"]})

            # Act
            result = self.data_service.get_fun_fact()

            # Assert
            self.assertIn(result, ["Fact 1", "Fact 2"])

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_fun_fact_with_file_not_found(self, mock_open):
        # Act
        result = self.data_service.get_fun_fact()

        # Assert
        self.assertEqual(result, "Where are all the MFA facts :(")

    def test_is_system_show_notification(self):
        # Act
        result = self.data_service.is_system_show_notification()

        # Assert
        self.assertTrue(result)

    def test_set_system_show_notification(self):
        # Act
        self.data_service.set_system_show_notification(False)

        # Assert
        self.assertTrue(self.data_service.signal_update)
        self.assertFalse(self.data_service.user_preference.show_notification)
        self.message_service_mock.send.assert_called_once_with(self.data_service, "Update Notification", False)


class TestDataServiceSection(unittest.TestCase):
    @patch.object(DataService, 'read_notes_titles')
    @patch('builtins.open')
    @patch('os.path.exists')
    def setUp(self, mock_path_exists, mock_open, mock_read_notes_titles):
        # Mock the MessageService instance
        self.message_service_mock = MagicMock(spec=MessageService)

        mock_path_exists.return_value = True
        data =  data = {"user": {"coins": 400, "quiz_completed": 0, "simulation_played": 0, "recent_activities": [], "badges": [], "improvements": [], "readings": [["title1", False], ["title2", False]], "unlocked_simulations": {"1": True, "2": False, "3": False, "4": False, "5": False, "6": False, "7": False}}, "user_preference": {"start_up_index": 0, "custom_quiz_setting_expand": False, "show_notification": True}}
        mock_file_content = json.dumps(data)
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        mock_read_notes_titles.return_value = []
        # Create a DataService instance
        self.data_service = DataService(self.message_service_mock)

    @patch('builtins.open')
    @patch('json.load')
    def test_get_simulation_details_existing(self, mock_json_load, mock_open):
        # Arrange
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_json_load.return_value = {"name": "Simulation", "details": "Details"}

        # Act
        result = self.data_service.get_simulation_details("existing_simulation")

        # Assert
        self.assertEqual(result, {"name": "Simulation", "details": "Details"})
        mock_open.assert_called_once_with(f'{Settings.SIMULATION_NOTE_PATH}existing_simulation.json', 'r')
        mock_json_load.assert_called_once()

    @patch('builtins.open')
    def test_get_simulation_details_non_existing(self, mock_open):
        # Arrange
        mock_open.side_effect = FileNotFoundError

        # Act
        result = self.data_service.get_simulation_details("non_existing_simulation")

        # Assert
        self.assertEqual(result, {})
        mock_open.assert_called_once_with(f'{Settings.SIMULATION_NOTE_PATH}non_existing_simulation.json', 'r')

    @patch('builtins.open')
    def test_get_simulation_details_cached(self, mock_open):
        # Arrange
        self.data_service.cached_details = {"exist": {"name": "Simulation", "details": "Details"}}

        # Act
        result = self.data_service.get_simulation_details("exist")

        # Assert
        self.assertEqual(result, {"name": "Simulation", "details": "Details"})
        mock_open.assert_not_called()


    @patch('builtins.open')
    @patch('json.load')
    def test_get_security_questions_existing(self, mock_json_load, mock_open):
        # Arrange
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_json_load.return_value = {"security_questions": ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5", "Question 6", "Question 7", "Question 8", "Question 9", "Question 10"]}

        # Act
        result = self.data_service.get_security_questions()

        # Assert
        self.assertEqual(len(result), 9)  # Ensure 9 questions are returned
        self.assertEqual(len(self.data_service.cached_security_questions), 10)
        mock_open.assert_called_once_with(Settings.SECURITY_QUESTION_FILE_PATH, 'r')
        mock_json_load.assert_called_once()

    @patch('builtins.open')
    def test_get_security_questions_non_existing(self, mock_open):
        # Arrange
        mock_open.side_effect = FileNotFoundError

        # Act
        result = self.data_service.get_security_questions()

        # Assert
        self.assertEqual(result, [])
        mock_open.assert_called_once_with(Settings.SECURITY_QUESTION_FILE_PATH, 'r')

    @patch('builtins.open')
    def test_get_security_questions_cached(self, mock_open):
        # Arrange
        self.data_service.cached_security_questions = ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5", "Question 6", "Question 7", "Question 8", "Question 9"]

        # Act
        result = self.data_service.get_security_questions()

        # Assert
        self.assertEqual(len(result), len(self.data_service.cached_security_questions))
        mock_open.assert_not_called()

    
    @patch('os.listdir')
    def test_read_notes_titles(self, mock_listdir):
        # Arrange
        mock_listdir.return_value = ['OTP.md', 'pin_card.md', 'the_best_reading.md']

        # Act
        result = self.data_service.read_notes_titles()

        # Assert
        self.assertEqual(len(result), 3)  # Ensure correct number of notes are returned
        self.assertTrue(all(isinstance(note, Note) for note in result))  # Ensure all elements are Note objects
        self.assertEqual(result[0].title, "OTP")  # Ensure titles are correctly formatted
        self.assertEqual(result[1].title, "Pin Card")
        self.assertEqual(result[2].title, "The Best Reading")

    @patch('os.listdir')
    @patch('builtins.open')
    def test_read_note_content(self, mock_open, mock_listdir):
        # Arrange
        mock_file = MagicMock()
        mock_file.read.return_value = "Note content"
        mock_open.return_value.__enter__.return_value = mock_file
        self.data_service.notes = [Note("Note1", ""), Note("Note2", ""), Note("Note3", "")]

        # Act
        result = self.data_service.read_note_content(0)

        # Assert
        self.assertEqual(result, "<p>Note content</p>")  # Ensure correct content is returned
        self.assertEqual(self.data_service.notes[0].content, "<p>Note content</p>")  # Ensure content is cached

    def test_get_notes(self):
        # Arrange
        self.data_service.notes = [Note("Note1", "1"), Note("Note2", "2"), Note("Note3", "3")]

        # Act
        result = self.data_service.get_notes()

        # Assert
        self.assertEqual(len(result), 3)  # Ensure correct number of notes are returned
        self.assertTrue(all(isinstance(note, Note) for note in result))  # Ensure all elements are Note objects
        self.assertEqual(result[0].title, "Note1")  # Ensure correct titles are returned
        self.assertEqual(result[1].title, "Note2")
        self.assertEqual(result[2].title, "Note3")
        self.assertEqual(result[0].content, "<p>1</p>")  # Ensure correct content are returned
        self.assertEqual(result[1].content, "<p>2</p>")
        self.assertEqual(result[2].content, "<p>3</p>")


    @patch('builtins.open')
    def test_get_quiz_bank_existing(self, mock_open):
        # Arrange
        mock_file_content = [{"question": "Question 1", "answer": "Answer 1"},
                             {"question": "Question 2", "answer": "Answer 2"}]
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_file_content)

        # Act
        result = self.data_service.get_quiz_bank()

        # Assert
        self.assertEqual(result, mock_file_content)
        self.assertEqual(result, self.data_service.cached_quiz_bank)
        mock_open.assert_called_once_with(Settings.QUIZ_FILE_PATH + 'quiz_bank1.json', 'r')

    @patch('builtins.open')
    def test_get_quiz_bank_cached(self, mock_open):
        # Arrange
        self.data_service.cached_quiz_bank = [{"question": "Question 1", "answer": "Answer 1"}]

        # Act
        result = self.data_service.get_quiz_bank()

        # Assert
        self.assertEqual(result, self.data_service.cached_quiz_bank)
        mock_open.assert_not_called()


    @patch('builtins.open')
    def test_get_help_token_existing(self, mock_open):
        # Arrange
        mock_file_content = {"0": "help token", "1": "token help"}
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_file_content)

        # Act
        result = self.data_service.get_help_token()

        # Assert
        self.assertEqual(result, (self.data_service.cache_help_index, mock_file_content))
        mock_open.assert_called_once_with(Settings.HELP_TOKEN_FILE_PATH, 'r')

    @patch('builtins.open')
    def test_get_help_token_cached(self, mock_open):
        # Arrange
        self.data_service.cache_help_index = {"word": "0"}

        # Act
        result = self.data_service.get_help_token()

        # Assert
        self.assertEqual(result, (self.data_service.cache_help_index, None))
        mock_open.assert_not_called()


    

    
