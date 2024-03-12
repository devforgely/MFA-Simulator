import unittest
from unittest.mock import MagicMock, patch
from viewmodels.main_viewmodel import MainViewModel, InfoBarIcon


class TestMainViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.data_service')
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock, data_service_mock):
        self.view_model = MainViewModel()

        # Mocking the DataService methods
        data_service_mock.return_value.get_fun_fact.return_value = "Fun fact"
        data_service_mock.return_value.get_user_coins.return_value = 10
        data_service_mock.return_value.get_user_badges_count.return_value = (1, 3)
        data_service_mock.return_value.get_system_start_up.return_value = 0

    def test_on_message_update_coins_earned(self):
        # Mocking change signals
        self.view_model.coin_count_changed = MagicMock()
        self.view_model.info_bar_added = MagicMock()

        # Emitting the "Update Coins" message with coins earned
        self.view_model.on_message("Update Coins", 20, True)

        # Asserting if the coin count changed signal is emitted with the correct value
        self.view_model.coin_count_changed.emit.assert_called_once_with("20")

        # Asserting if an info bar with coin icon is added
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.COIN, "You've just earned some coins!")

    def test_on_message_update_coins_not_earned(self):
        # Mocking change signals
        self.view_model.coin_count_changed = MagicMock()
        self.view_model.info_bar_added = MagicMock()

        # Emitting the "Update Coins" message with no coins earned
        self.view_model.on_message("Update Coins", 20, False)

        # Asserting if the coin count changed signal is emitted with the correct value
        self.view_model.coin_count_changed.emit.assert_called_once_with("20")

        # Asserting that no info bar is added
        self.assertFalse(self.view_model.info_bar_added.emit.called)

    def test_on_message_insufficient_coins(self):
        # Mocking change signals
        self.view_model.coin_count_changed = MagicMock()
        self.view_model.info_bar_added = MagicMock()

        # Emitting the "Insufficient Coins" message
        self.view_model.on_message("Insufficient Coins", 30)

        # Asserting that an info bar with warning icon is added
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.WARNING, "Requires 30 more coins.")

    def test_on_message_update_badges(self):
        # Mocking change signals
        self.view_model.badge_count_changed = MagicMock()
        self.view_model.info_bar_added = MagicMock()
        
        # Emitting the "Update Badges" message
        self.view_model.on_message("Update Badges", (1, 3), "Gold")

        # Asserting if the badge count changed signal is emitted with the correct value
        self.view_model.badge_count_changed.emit.assert_called_once_with("1/3")

        # Asserting if an info bar with medal icon is added
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.MEDAL, "You've been awarded with Gold MFA badge!")

    def test_on_message_success_notification(self):
        # Mocking change signal
        self.view_model.info_bar_added = MagicMock()

        # Emitting the "Success Notification" message
        self.view_model.on_message("Success Notification", "Success message")

        # Asserting if an info bar with success icon is added
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.SUCCESS, "Success message")

    def test_on_message_warning_notification(self):
        # Mocking change signal
        self.view_model.info_bar_added = MagicMock()

        # Emitting the "Warning Notification" message
        self.view_model.on_message("Warning Notification", "Warning message")

        # Asserting if an info bar with warning icon is added
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.WARNING, "Warning message")

    def test_on_message_error_notification(self):
        # Mocking change signal
        self.view_model.info_bar_added = MagicMock()

        # Emitting the "Error Notification" message
        self.view_model.on_message("Error Notification", "Error message")

        # Asserting if an info bar with error icon is added
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.ERROR, "Error message")

    def test_on_message_update_notification(self):
        # Mocking change signal
        self.view_model.info_bar_added = MagicMock()

        self.view_model.is_show_notification = False

        # Emitting the "Update Notification" message
        self.view_model.on_message("Update Notification", True)

        # Asserting that the is_show_notification attribute is updated
        self.assertTrue(self.view_model.is_show_notification)

    def test_fact(self):
        # Mocking change signal
        self.view_model.fact_changed = MagicMock()

        # Calling the fact method
        self.view_model.fact()

        # Asserting if the fact changed signal is emitted with the correct value
        self.view_model.fact_changed.emit.assert_called_once_with("Fun fact")

    def test_coin_count(self):
        # Mocking change signal
        self.view_model.coin_count_changed = MagicMock()

        # Calling the coin_count method
        self.view_model.coin_count()

        # Asserting if the coin count changed signal is emitted with the correct value
        self.view_model.coin_count_changed.emit.assert_called_once_with("10")

    def test_badge_count(self):
        # Mocking change signal
        self.view_model.badge_count_changed = MagicMock()

        # Calling the badge_count method
        self.view_model.badge_count()

        # Asserting if the badge count changed signal is emitted with the correct value
        self.view_model.badge_count_changed.emit.assert_called_once_with("1/3")

    def test_add_info_bar_show_notification(self):
        # Mocking change signal
        self.view_model.info_bar_added = MagicMock()

        # Enabling notification
        self.view_model.is_show_notification = True

        # Calling the add_info_bar method
        self.view_model.add_info_bar(InfoBarIcon.WARNING, "Warning message")

        # Asserting if the info bar added signal is emitted with the correct parameters
        self.view_model.info_bar_added.emit.assert_called_once_with(InfoBarIcon.WARNING, "Warning message")

    def test_add_info_bar_hide_notification(self):
        # Mocking change signal
        self.view_model.info_bar_added = MagicMock()

        # Disabling notification
        self.view_model.is_show_notification = False

        # Calling the add_info_bar method
        self.view_model.add_info_bar(InfoBarIcon.WARNING, "Warning message")

        # Asserting that no info bar is added
        self.assertFalse(self.view_model.info_bar_added.emit.called)

    def test_get_system_startup(self):
        # Calling the get_system_startup method
        system_startup = self.view_model.get_system_startup()

        # Asserting if the returned value matches the mocked system startup value
        self.assertEqual(system_startup, 0)

    def test_help(self):
        # Calling the help method
        self.view_model.help()

        # Asserting if the message service send method is called with the correct parameters
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Help")

    

    
