import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.fingerprint_viewmodel import FingerprintRegisterViewModel, FingerprintAuthenticateViewModel
import numpy as np

class TestFingerprintRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = FingerprintRegisterViewModel()

    def test_on_finger_changed(self):
        # Mock the button
        mock_button = MagicMock()
        mock_button.objectName.return_value = "fp1_btn"
        
        # Call the method with checked=True
        self.viewmodel.on_finger_changed(mock_button, True)
        
        # Assert that the current_finger is set correctly
        self.assertEqual(self.viewmodel.current_finger, "fp1")

    def test_set_fingerprint(self):
        # mock signals
        self.viewmodel.fingerprint_progress = MagicMock()
        self.viewmodel.send = MagicMock()

        # Case: Different finger selected
        self.viewmodel.prev_finger = "fp1"
        self.viewmodel.current_finger = "fp2"
        self.viewmodel.set_fingerprint()
        self.assertEqual(self.viewmodel.progress, 0)
        self.assertEqual(self.viewmodel.prev_finger, "fp2")
        self.viewmodel.fingerprint_progress.emit.assert_called_with("0")

        # Case: Same finger selected, progress less than 6
        self.viewmodel.fingerprint_progress.reset_mock()
        self.viewmodel.prev_finger = "fp1"
        self.viewmodel.current_finger = "fp1"
        self.viewmodel.set_fingerprint()
        self.assertTrue(self.viewmodel.progress >= 0 and self.viewmodel.progress < 6)
        self.viewmodel.fingerprint_progress.emit.assert_called()
        
        # Case: Same finger selected, progress reaches 6
        self.viewmodel.progress = 5
        self.viewmodel.set_fingerprint()
        self.assertEqual(self.viewmodel.progress, 6)
        self.viewmodel.send.assert_called()

    def test_state_data(self):
        mock_data = {
            "user_fingerprint": b"user_fingerprint",
            "fingerprint_template": np.array([1, 2, 3, 4, 5])
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["user_fingerprint"], str))
        self.assertTrue(isinstance(result["fingerprint_template"], str))

    @patch('viewmodels.authentication.fingerprint_viewmodel.image_byte', return_value=b"fingerprint")
    def test_send(self, mock_image_byte):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Registration successful
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send("fingerprint_path")
        self.viewmodel.state_change.emit.assert_called_with("Fingerprint added", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send("fingerprint_path")
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)


class TestFingerprintAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = FingerprintAuthenticateViewModel()

    
    def test_on_finger_changed(self):
        # Mock the button
        mock_button = MagicMock()
        mock_button.objectName.return_value = "fp1_btn"
        
        # Call the method with checked=True
        self.viewmodel.on_finger_changed(mock_button, True)
        
        # Assert that the current_finger is set correctly
        self.assertEqual(self.viewmodel.current_finger, "fp1")

    def test_state_data(self):
        mock_data = {
            "fingerprint": b"user_fingerprint",
            "fingerprint_template": np.array([1, 2, 3, 4, 5]),
            "similarity_score": 0.99
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data(False)
        self.assertTrue(isinstance(result["fingerprint_template"], str))

        result = self.viewmodel.state_data(True)
        self.assertTrue(isinstance(result["fingerprint_template"], str))
        self.assertTrue(isinstance(result["fingerprint"], str))
        self.assertTrue(isinstance(result["similarity_score"], str))

    @patch('viewmodels.authentication.fingerprint_viewmodel.image_byte', return_value=b"fingerprint")
    def test_send(self, mock_image_byte):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("The user has been authenticated.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(True), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")

        # Case: Incorrect
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Your credentials does not match our records.", 1)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 2)

    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.bypass()
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)


    