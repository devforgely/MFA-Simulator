import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.twofa_key_viewmodel import TwoFAKeyRegisterViewModel, TwoFAKeyAuthenticateViewModel
import numpy as np


class TestFingerprintRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = TwoFAKeyRegisterViewModel()

    def test_on_finger_changed(self):
        # Mock the button
        mock_button = MagicMock()
        mock_button.objectName.return_value = "fp3_btn"
        
        # Call the method with checked=True
        self.viewmodel.on_finger_changed(mock_button, True)
        
        # Assert that the current_finger is set correctly
        self.assertEqual(self.viewmodel.current_finger, "fp3")

    def test_prepare_fingerprint(self):
        # mock signals
        self.viewmodel.allow_fingerprint = MagicMock()

        # Case: Key name less than 3 characters
        self.viewmodel.prepare_fingerprint("ab")
        self.viewmodel.allow_fingerprint.emit.assert_called_with(False)

        # Case: Key name with 3 or more characters
        self.viewmodel.prepare_fingerprint("abc")
        self.viewmodel.allow_fingerprint.emit.assert_called_with(True)   
    
    def test_set_fingerprint(self):
        # mock signals
        self.viewmodel.key_on = True
        self.viewmodel.allow_fingerprint = MagicMock()
        self.viewmodel.fingerprint_progress = MagicMock()
        self.viewmodel.send = MagicMock()

        # Case: Different finger selected
        self.viewmodel.current_finger = "fp4"
        self.viewmodel.set_fingerprint()
        self.assertEqual(self.viewmodel.progress, 0)
        self.assertEqual(self.viewmodel.prev_finger, "fp4")
        self.viewmodel.fingerprint_progress.emit.assert_called_with("0")

        # Case: Same finger selected, progress less than 5
        self.viewmodel.fingerprint_progress.reset_mock()
        self.viewmodel.current_finger = "fp4"
        self.viewmodel.progress = 3
        self.viewmodel.set_fingerprint()
        self.assertTrue(self.viewmodel.progress >= 0 and self.viewmodel.progress <= 5)
        self.viewmodel.fingerprint_progress.emit.assert_called()

        # Case: Same finger selected, progress reaches 5
        self.viewmodel.progress = 4
        self.viewmodel.set_fingerprint()
        self.assertEqual(self.viewmodel.progress, 5)
        self.viewmodel.send.assert_called()

    @patch('viewmodels.authentication.twofa_key_viewmodel.decode_key', return_value="data")
    def test_state_data(self, mock_decode_key):
        # Mock session stored data
        mock_data = {
            "user_fingerprint": b"user_fingerprint",
            "fingerprint_template": np.array([1, 2, 3, 4, 5]),
            "private_key": b"private_key",
            "public_key": b"public_key"
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        # Call the method under test
        result = self.viewmodel.state_data()

        # Assertions
        self.assertTrue(isinstance(result["user_fingerprint"], str))
        self.assertTrue(isinstance(result["fingerprint_template"], str))
        self.assertTrue(isinstance(result["private_key"], str))
        self.assertTrue(isinstance(result["public_key"], str))

    @patch('viewmodels.authentication.twofa_key_viewmodel.image_byte', return_value=b"fingerprint")
    def test_send(self, mock_image_byte):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Registration successful
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send("key_name", "fingerprint_path")
        self.viewmodel.state_change.emit.assert_called_with("Registration Completed", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send("key_name", "fingerprint_path")
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)


class TestTwoFAKeyAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service):
        self.viewmodel = TwoFAKeyAuthenticateViewModel()

    def test_on_finger_changed(self):
        # Mock the button
        mock_button = MagicMock()
        mock_button.objectName.return_value = "fp4_btn"
        
        # Call the method with checked=True
        self.viewmodel.on_finger_changed(mock_button, True)
        
        # Assert that the current_finger is set correctly
        self.assertEqual(self.viewmodel.current_finger, "fp4")

    @patch('viewmodels.authentication.twofa_key_viewmodel.decode_key', return_value="data")
    def test_state_data(self, mock_decode_key):
        # Mock session stored data
        mock_data = {
            "fingerprint_template": np.array([1, 2, 3, 4, 5]),
            "private_key": b"private_key",
            "public_key": b"public_key",
            "fingerprint": b"fingerprint",
            "similarity_score": 0.99,
            "nonce": b"nonce",
            "signed_challenge": b"signed_challenge",
            "key_name": "key_name"
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        # Call the method under test with is_checked=False
        result = self.viewmodel.state_data(False)

        # Assertions
        self.assertTrue(isinstance(result["fingerprint_template"], str))
        self.assertTrue(isinstance(result["private_key"], str))
        self.assertTrue(isinstance(result["public_key"], str))
        self.assertTrue(isinstance(result["fingerprint"], str))
        self.assertTrue(isinstance(result["similarity_score"], str))

        # Call the method under test with is_checked=True
        result = self.viewmodel.state_data(True)

        # Assertions
        self.assertTrue(isinstance(result["fingerprint_template"], str))
        self.assertTrue(isinstance(result["private_key"], str))
        self.assertTrue(isinstance(result["public_key"], str))
        self.assertTrue(isinstance(result["fingerprint"], str))
        self.assertTrue(isinstance(result["similarity_score"], str))
        self.assertTrue(isinstance(result["nonce"], str))
        self.assertTrue(isinstance(result["signed_challenge"], str))

    @patch('viewmodels.authentication.twofa_key_viewmodel.image_byte', return_value=b"fingerprint")
    def test_send(self, mock_image_byte):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.key_on = True
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("The user has been authenticated.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(True), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")

        # Case: Incorrect
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.key_on = True
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Your credentials do not match our record.", 1)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.key_on = True
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 2)

    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Call the method under test
        self.viewmodel.bypass()

        # Assertion
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)