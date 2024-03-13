import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.password_viewmodel import PasswordRegisterViewModel, PasswordAuthenticateViewModel

class TestPasswordRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = PasswordRegisterViewModel()

    def test_update_security_level(self):
        spy = MagicMock()
        self.viewmodel.scurity_measure_changed.connect(spy)

        # Case: Low security level
        self.viewmodel.update_security_level("password")
        spy.assert_called_once_with(30)

        # Case: Medium security level
        self.viewmodel.update_security_level("Pa55w0rd")
        spy.assert_called_with(57)

        # Case: High security level
        self.viewmodel.update_security_level("Str0ngP@ssw0rd!m")
        spy.assert_called_with(92)

    def test_state_data(self):
        mock_data = {
            "hashed_secret": b"secret",
            "salt": b"salt"
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertTrue(isinstance(result["salt"], str))

    def test_send(self):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Credentials too short
        self.viewmodel.send("user", "pw", "pw")
        self.viewmodel.state_change.emit.assert_called_with("Credentials is too short.", 1)

        # Case: Passwords do not match
        self.viewmodel.send("user", "password", "different")
        self.viewmodel.state_change.emit.assert_called_with("Passwords do NOT match.", 1)

        # Case: Registration successful
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send("user", "Pa55w0rd", "Pa55w0rd")
        self.viewmodel.state_change.emit.assert_called_with("Account has been registered.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with({}, 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send("user", "Pa55w0rd", "Pa55w0rd")
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)


class TestPasswordAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = PasswordAuthenticateViewModel()

    def test_state_data(self):
        mock_data = {
            "hashed_secret": b"secret",
            "salt": b"salt"
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertTrue(isinstance(result["salt"], str))

    def test_send(self):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.send("username", "Password")
        self.viewmodel.state_change.emit.assert_called_with("The user has been authenticated.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(True), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")

        # Case: Incorrect
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.send("username", "Password")
        self.viewmodel.state_change.emit.assert_called_with("These credentials does not match our records.", 1)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.send("username", "Password")
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 2)

    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.bypass()
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)

    