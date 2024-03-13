import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.totp_viewmodel import TOTPRegisterViewModel, TOTPAuthenticateViewModel

class TestTOTPRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = TOTPRegisterViewModel()

    def test_generate_ip(self):
        ip = self.viewmodel.generate_ip()
        self.assertTrue(ip)
        self.assertIsInstance(ip, str)

    def test_generate_user_id(self):
        user_id = self.viewmodel.generate_user_id()
        self.assertTrue(user_id)
        self.assertIsInstance(user_id, str)

    def test_scan_qr(self):
        # mock signals
        self.viewmodel.qr_scan_signal = MagicMock()

        self.viewmodel.scan_qr()

        # Assertions
        self.viewmodel.qr_scan_signal.emit.assert_called_once()

    def test_state_data(self):
        # Mocking session stored data
        mock_data = {"key": "value"}
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        # Test
        result = self.viewmodel.state_data()

        # Assertion
        self.assertEqual(result, mock_data)

    def test_send(self):
        # Mocking signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Registration successful
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Account is linked.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with({}, 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)
        self.viewmodel.state_data_change.emit.not_called()


class TestTOTPAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = TOTPAuthenticateViewModel()

    def test_get_code(self):
        self.viewmodel.code_changed = MagicMock()

        # Mocking session stored data
        self.viewmodel.authentication_service.get_session_stored.return_value = {"totp": "123456"}

        # Call the method under test
        self.viewmodel.get_code()

        # Assertions
        self.viewmodel.code_changed.emit.assert_called_once()

    @patch.object(TOTPAuthenticateViewModel, 'get_code')
    def test_start_totp(self, mock_get_code):
        self.viewmodel.threading = MagicMock()

        # Call the method under test
        self.viewmodel.start_totp()

        # Assertions
        self.assertTrue(mock_get_code.called)
        self.assertTrue(self.viewmodel.threading.set_max.called)
        self.assertTrue(self.viewmodel.threading.start.called)

    @patch.object(TOTPAuthenticateViewModel, 'get_code')
    def test_signal_update(self, mock_get_code):
        self.viewmodel.time_changed = MagicMock()
        self.viewmodel.threading = MagicMock()

        # Call the method under test
        self.viewmodel.signal_update(10)

        # Assertions
        self.assertFalse(mock_get_code.called)
        self.viewmodel.time_changed.emit.assert_called_once_with(10)

    def test_send(self):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.send("1111")
        self.viewmodel.state_change.emit.assert_called_with("The user has been authenticated.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(True), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")

        # Case: Incorrect
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.send("1111")
        self.viewmodel.state_change.emit.assert_called_with("The TOTP does not match.", 1)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.send("1111")
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 2)

    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.bypass()
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)