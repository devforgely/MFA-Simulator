import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.chip_pin_viewmodel import ChipPinRegisterViewModel, ChipPinAuthenticateViewModel
import uuid

class TestChipPinRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = ChipPinRegisterViewModel()

    def test_generate_pin(self):
        spy = MagicMock()
        self.viewmodel.pin_field_changed.connect(spy)

        self.viewmodel.generate_pin()

        self.assertTrue(spy.called)
        args = spy.call_args[0]
        self.assertTrue(args[0].isdigit())
        self.assertEqual(len(args[0]), 6)

    def test_update_pin_field(self):
        spy = MagicMock()
        self.viewmodel.pin_field_changed.connect(spy)

        self.viewmodel.update_pin_field("", "1")

        self.assertTrue(spy.called)
        args = spy.call_args[0]
        self.assertEqual(args[0], "1")

    def test_state_data(self):
        id = uuid.uuid4()
        mock_data = {
            "hashed_pin": b"hashed_pin",
            "chip_details": id,
            "chip_digital_signature": b"chip_digital_signature"
        }

        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["hashed_pin"], str))
        self.assertEqual(result["chip_details"], str(id))
        self.assertTrue(isinstance(result["chip_digital_signature"], str))

    def test_send(self):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.pin_field_changed = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: PIN must be at least 4 digits long
        self.viewmodel.send("123")
        self.viewmodel.state_change.emit.assert_called_with("PIN must be at least 4 digits long.", 1)

        # Case: First PIN check
        self.viewmodel.send("1234")
        self.assertEqual(self.viewmodel.pin_entered, "1234")
        self.viewmodel.state_change.emit.assert_called_with("", 2)
        self.viewmodel.pin_field_changed.emit.assert_called_with("")

        # Case: PIN did not match
        self.viewmodel.send("4321")
        self.assertEqual(self.viewmodel.pin_entered, "")
        self.viewmodel.state_change.emit.assert_called_with("PIN did not match.", 3)
        self.viewmodel.pin_field_changed.emit.assert_called_with("")

        # Case: Registration restart
        self.viewmodel.send("1234")
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send("1234")
        self.viewmodel.state_change.emit.assert_called_with("Account registered and card received.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with({}, 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.send("1234")
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send("1234")
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)


class TestChipPinAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = ChipPinAuthenticateViewModel()

    def test_update_pin_field(self):
        spy = MagicMock()
        self.viewmodel.pin_field_changed.connect(spy)

        self.viewmodel.allow_pin = True
        self.viewmodel.update_pin_field("", "1")

        self.assertTrue(spy.called)
        args = spy.call_args[0]
        self.assertEqual(args[0], "1")


    def test_state_data(self):
        id = uuid.uuid4()
        mock_data = {
            "hashed_pin": b'hashed_pin',
            "chip_details": id,
            "chip_digital_signature": b'chip_digital_signature',
            "arqc": b'arqc',
            "arpc": b'arpc'
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data
    
        result = self.viewmodel.state_data(False)
        self.assertTrue(isinstance(result["hashed_pin"], str))
        self.assertEqual(result["chip_details"], str(id))
        self.assertTrue(isinstance(result["chip_digital_signature"], str))

        result = self.viewmodel.state_data(True)
        self.assertTrue(isinstance(result["hashed_pin"], str))
        self.assertEqual(result["chip_details"], str(id))
        self.assertTrue(isinstance(result["chip_digital_signature"], str))
        self.assertTrue(isinstance(result["arqc"], str))
        self.assertTrue(isinstance(result["arpc"], str))

    def test_send(self):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.send("1234")
        self.viewmodel.state_change.emit.assert_called_with("The user has been authenticated.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(True), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")

        # Case: Incorrect PIN entered
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.send("5678")
        self.viewmodel.state_change.emit.assert_called_with("Incorrect PIN entered", 1)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.send("9101")
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 2)

    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.bypass()
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)

        