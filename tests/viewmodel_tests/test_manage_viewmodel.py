import unittest
from unittest.mock import MagicMock, patch
from viewmodels.manage_viewmodel import ManageViewModel

class TestManageViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.data_service')
    def setUp(self, data_service_mock):
        self.view_model = ManageViewModel()

        # Mocking the DataService methods
        data_service_mock.return_value.get_system_start_up.return_value = 0
        data_service_mock.return_value.get_custom_quiz_setting_expand.return_value = False
        data_service_mock.return_value.is_system_show_notification.return_value = True

    def test_start_up_index(self):
        # Mocking change signal
        self.view_model.start_up_changed = MagicMock()

        # Calling the start_up_index method
        self.view_model.start_up_index()

        # Asserting if the start_up_changed signal is emitted with the correct value
        self.view_model.start_up_changed.emit.assert_called_once_with(0)

    def test_quiz_expand_toggle(self):
        # Mocking change signal
        self.view_model.quiz_expand_changed = MagicMock()

        # Calling the quiz_expand_toggle method
        self.view_model.quiz_expand_toggle()

        # Asserting if the quiz_expand_changed signal is emitted with the correct value
        self.view_model.quiz_expand_changed.emit.assert_called_once_with(False)

    def test_notification_toggle(self):
        # Mocking change signal
        self.view_model.notification_toggle_changed = MagicMock()

        # Calling the notification_toggle method
        self.view_model.notification_toggle()

        # Asserting if the notification_toggle_changed signal is emitted with the correct value
        self.view_model.notification_toggle_changed.emit.assert_called_once_with(True)

    def test_change_start_up_index(self):
        # Calling the change_start_up_index method with a new index
        self.view_model.change_start_up_index(1)

        # Asserting if the data service's change_system_start_up method is called with the correct parameter
        self.view_model.data_service.change_system_start_up.assert_called_once_with(1)

    def test_change_quiz_expand(self):
        # Calling the change_quiz_expand method with a new state
        self.view_model.change_quiz_expand(True)

        # Asserting if the data service's change_custom_quiz_setting_expand method is called with the correct parameter
        self.view_model.data_service.change_custom_quiz_setting_expand.assert_called_once_with(True)

    def test_change_notification_state(self):
        # Calling the change_notification_state method with a new state
        self.view_model.change_notification_state(False)

        # Asserting if the data service's set_system_show_notification method is called with the correct parameter
        self.view_model.data_service.set_system_show_notification.assert_called_once_with(False)

    def test_reset_application(self):
        # Calling the reset_application method
        self.view_model.reset_application()

        # Asserting if the data service's reset_data method is called
        self.view_model.data_service.reset_data.assert_called_once()