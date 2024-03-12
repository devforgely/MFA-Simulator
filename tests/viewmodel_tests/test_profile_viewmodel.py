import unittest
from unittest.mock import MagicMock, patch
from viewmodels.profile_viewmodel import ProfileViewModel

class TestProfileViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.data_service')
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock, data_service_mock):
        self.view_model = ProfileViewModel()

        # Mocking the DataService methods
        data_service_mock.return_value.get_user_coins.return_value = 10
        data_service_mock.return_value.get_user_quiz_completed.return_value = 5
        data_service_mock.return_value.get_user_simulation_played.return_value = 3
        data_service_mock.return_value.get_user_recent_activiies.return_value = ["Activity 1", "Activity 2"]
        data_service_mock.return_value.get_user_badges.return_value = ["Badge 1", "Badge 2"]
        data_service_mock.return_value.get_user_improvements.return_value = ["Improvement 1", "Improvement 2"]
        data_service_mock.return_value.get_user_readings.return_value = [("Book 1", True), ("Book 2", False)]

    def test_on_message_update_coins(self):
        # Mocking change signal
        self.view_model.coin_changed = MagicMock()

        # Emitting the "Update Coins" message with new coin value
        self.view_model.on_message("Update Coins", 20)

        # Asserting if the coin changed signal is emitted with the correct value
        self.view_model.coin_changed.emit.assert_called_once_with("20")

    def test_on_message_update_quiz(self):
        # Mocking change signals
        self.view_model.quiz_amount_changed = MagicMock()
        self.view_model.acitivites = MagicMock()

        # Emitting the "Update Quiz" message with new quiz amount
        self.view_model.on_message("Update Quiz", 8)

        # Asserting if the quiz amount changed signal is emitted with the correct value
        self.view_model.quiz_amount_changed.emit.assert_called_once_with("8")

        # Asserting if the acitivites method is called
        self.view_model.acitivites.assert_called_once()

    def test_on_message_update_simulation(self):
        # Mocking change signals
        self.view_model.simulation_amount_changed = MagicMock()
        self.view_model.acitivites = MagicMock()

        # Emitting the "Update Simulation" message with new simulation amount
        self.view_model.on_message("Update Simulation", 6)

        # Asserting if the simulation amount changed signal is emitted with the correct value
        self.view_model.simulation_amount_changed.emit.assert_called_once_with("6")

        # Asserting if the acitivites method is called
        self.view_model.acitivites.assert_called_once()

    def test_on_message_update_improvements(self):
        # Mocking change signal
        self.view_model.improvements = MagicMock()

        # Emitting the "Update Improvements" message
        self.view_model.on_message("Update Improvements")

        # Asserting if the improvements method is called
        self.view_model.improvements.assert_called_once()

    def test_on_message_update_badges(self):
        # Mocking change signal
        self.view_model.badges = MagicMock()

        # Emitting the "Update Badges" message
        self.view_model.on_message("Update Badges")

        # Asserting if the badges method is called
        self.view_model.badges.assert_called_once()

    def test_coin(self):
        # Mocking change signal
        self.view_model.coin_changed = MagicMock()

        # Calling the coin method
        self.view_model.coin()

        # Asserting if the coin changed signal is emitted with the correct value
        self.view_model.coin_changed.emit.assert_called_once_with("10")

    def test_quiz_amount(self):
        # Mocking change signal
        self.view_model.quiz_amount_changed = MagicMock()

        # Calling the quiz_amount method
        self.view_model.quiz_amount()

        # Asserting if the quiz amount changed signal is emitted with the correct value
        self.view_model.quiz_amount_changed.emit.assert_called_once_with("5")

    def test_simulation_amount(self):
        # Mocking change signal
        self.view_model.simulation_amount_changed = MagicMock()

        # Calling the simulation_amount method
        self.view_model.simulation_amount()

        # Asserting if the simulation amount changed signal is emitted with the correct value
        self.view_model.simulation_amount_changed.emit.assert_called_once_with("3")

    def test_activities(self):
        # Mocking change signal
        self.view_model.acitivites_changed = MagicMock()

        # Calling the activities method
        self.view_model.acitivites()

        # Asserting if the activities changed signal is emitted with the correct value
        self.view_model.acitivites_changed.emit.assert_called_once_with(["Activity 1", "Activity 2"])

    def test_badges(self):
        # Mocking change signal
        self.view_model.badges_changed = MagicMock()

        # Calling the badges method
        self.view_model.badges()

        # Asserting if the badges changed signal is emitted with the correct value
        self.view_model.badges_changed.emit.assert_called_once_with(["Badge 1", "Badge 2"])

    def test_improvements(self):
        # Mocking change signal
        self.view_model.improvements_changed = MagicMock()

        # Calling the improvements method
        self.view_model.improvements()

        # Asserting if the improvements changed signal is emitted with the correct value
        self.view_model.improvements_changed.emit.assert_called_once_with(["Improvement 1", "Improvement 2"])

    def test_readings(self):
        # Mocking change signal
        self.view_model.readings_changed = MagicMock()

        # Calling the readings method
        self.view_model.readings()

        # Asserting if the readings changed signal is emitted with the correct value
        self.view_model.readings_changed.emit.assert_called_once_with([("Book 1", True), ("Book 2", False)])

    def test_update_reading(self):
        # Mocking DataService method
        self.view_model.data_service.update_user_reading = MagicMock()

        # Calling the update_reading method with mock parameters
        self.view_model.update_reading("Book && Life", 2, 0)

        # Asserting if the DataService method is called with the correct parameters
        self.view_model.data_service.update_user_reading.assert_called_once_with("Book & Life", True, 0)

    def test_update_reading_false(self):
        # Mocking DataService method
        self.view_model.data_service.update_user_reading = MagicMock()

        # Calling the update_reading method with mock parameters
        self.view_model.update_reading("Book && Life", 0, 0)

        # Asserting if the DataService method is called with the correct parameters
        self.view_model.data_service.update_user_reading.assert_called_once_with("Book & Life", False, 0)