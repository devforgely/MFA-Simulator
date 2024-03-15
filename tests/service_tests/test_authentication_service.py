import unittest
from unittest.mock import MagicMock
from services.authentication_service import AuthenticationService
from models.authentication.authentication import Method
from models.user import Badge

class TestAuthenticationService(unittest.TestCase):
    def setUp(self):
        self.data_service = MagicMock()
        self.service = AuthenticationService(self.data_service)

    def test_can_simulate(self):
        self.service.add(Method.PASSWORD)

        self.assertTrue(self.service.can_simulate())

    def test_can_simulate_false(self):
        self.assertFalse(self.service.can_simulate())

    def test_get_type(self):
        self.service.add(Method.TOTP)
        self.service.at = 0
        self.assertEqual(self.service.get_type(), Method.TOTP)

    def test_get_type_null(self):
        self.assertEqual(self.service.get_type(), Method.NULL)

    def test_get_all_type(self):
        self.assertTrue(self.service.add(Method.PASSWORD))
        self.assertTrue(self.service.add(Method.FINGERPRINT))
        self.assertEqual(len(self.service.get_all_types()), 2)

    def test_get_all_type_empty(self):
        self.assertEqual(len(self.service.get_all_types()), 0)

    def test_assurance_level(self):
        self.assertEqual(self.service.calculate_assurance_level(), 0)
        self.assertTrue(self.service.add(Method.PASSWORD))
        self.assertEqual(self.service.calculate_assurance_level(), 1)
        self.assertTrue(self.service.add(Method.SECRET_QUESTION))
        self.assertEqual(self.service.calculate_assurance_level(), 1)
        self.assertTrue(self.service.add(Method.FINGERPRINT))
        self.assertEqual(self.service.calculate_assurance_level(), 2)
        self.assertTrue(self.service.add(Method.TOTP))
        self.assertEqual(self.service.calculate_assurance_level(), 2)
        self.assertTrue(self.service.add(Method.TWOFA_KEY))
        self.assertEqual(self.service.calculate_assurance_level(), 3)

    def test_add_method(self):
        self.assertTrue(self.service.add(Method.PASSWORD))
        self.assertTrue(self.service.add(Method.FINGERPRINT))
        self.assertTrue(self.service.add(Method.TOTP))
        self.assertFalse(self.service.add(Method.PASSWORD))  # Adding the same method again should fail
        self.assertEqual(len(self.service.strategy), 3)

    def test_remove_method(self):
        self.service.add(Method.PASSWORD)
        self.assertTrue(self.service.remove(Method.PASSWORD))
        self.assertFalse(self.service.remove(Method.PASSWORD))  # Removing the same method again should fail
        self.assertEqual(len(self.service.strategy), 0)

    def test_register(self):
        self.service.add(Method.PASSWORD)
        self.assertEqual(self.service.register_count, 0)
        self.assertTrue(self.service.register("username", "password"))
        self.assertEqual(self.service.register_count, 1)
        self.assertTrue(self.service.register("username2", "password2"))
        self.assertEqual(self.service.register_count, 1)

    def test_authenticate_success(self):
        self.service.add(Method.PASSWORD)
        self.assertEqual(self.service.register_count, 0)
        self.service.register("username", "password")
        self.assertEqual(self.service.register_count, 1)
        self.assertEqual(self.service.auth_count, 0)
        self.assertEqual(self.service.authenticate("username", "password"), 0)
        self.assertEqual(self.service.auth_count, 1)

    def test_authenticate_fail(self):
        self.service.add(Method.PASSWORD)
        self.service.register("username", "password")
        self.assertEqual(self.service.authenticate("username", "wrong_password"), 1)

    def test_authenticate_lockout(self):
        self.service.add(Method.PASSWORD)
        self.service.register("username", "password")
        for _ in range(self.service.LIMIT_COUNT):
            self.assertEqual(self.service.authenticate("username", "wrong_password"), 1)
        # After LIMIT_COUNT attempts, authentication should be locked out
        self.assertEqual(self.service.authenticate("username", "wrong_password"), 2)

    def test_authenticate_lockout_ignore(self):
        self.service.add(Method.TOTP)
        self.service.register("")
        self.service.register("confirm")
        for _ in range(self.service.LIMIT_COUNT):
            self.assertEqual(self.service.authenticate("GENERATE"), 1)
        # After LIMIT_COUNT attempts, authentication should be locked out
        self.assertEqual(self.service.authenticate(self.service.get_session_stored()["totp"]), 2)
        # After LIMIT_COUNT attempts, authentication should be locked out but can ignore
        self.assertEqual(self.service.authenticate("GENERATE", ignore_limit=True), 1)
        self.assertEqual(self.service.authenticate(self.service.get_session_stored()["totp"], ignore_limit=True), 0)

    def test_forward(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.SECRET_QUESTION)
        self.assertEqual(self.service.at, 0)
        self.assertTrue(self.service.forward())
        self.assertEqual(self.service.at, 1)
        self.assertTrue(self.service.forward())
        self.assertEqual(self.service.at, 2)
        self.assertFalse(self.service.forward())
        self.assertEqual(self.service.at, 2)

    def test_backward(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.SECRET_QUESTION)
        self.service.at = 0
        self.assertFalse(self.service.backward())
        self.assertEqual(self.service.at, 0)
        self.service.at = 1
        self.assertTrue(self.service.backward())
        self.assertFalse(self.service.backward())
        self.assertEqual(self.service.at, 0)
        self.service.at = 6
        self.assertTrue(self.service.backward())
        self.assertEqual(self.service.at, 5)

    def test_all_registered(self):
        self.service.add(Method.PASSWORD)
        self.service.register("username", "password")
        self.assertTrue(self.service.all_registered())

        self.service.add(Method.CHIP_PIN)
        self.assertFalse(self.service.all_registered())

    def test_go_authenticate(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.CHIP_PIN)
        self.service.register("username", "password")
        self.assertFalse(self.service.go_authenticate())
        self.service.forward()
        self.service.register("1111")
        self.assertTrue(self.service.go_authenticate())
        self.service.forward()
        self.assertFalse(self.service.go_authenticate())

    def test_all_authenticated(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.CHIP_PIN)
        self.service.register("username", "password")
        self.service.authenticate("username", "password")
        self.service.forward()
        self.assertFalse(self.service.all_authenticated())
        self.service.register("1111")
        self.service.authenticate("1111")
        self.assertTrue(self.service.all_authenticated())

    def test_go_finish(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.CHIP_PIN)
        self.service.register("username", "password")
        self.service.authenticate("username", "password")
        self.assertFalse(self.service.go_finish())
        self.service.forward()
        self.service.register("1111")
        self.service.authenticate("1111")
        self.assertTrue(self.service.go_finish())

    def test_reset(self):
        self.service.add(Method.PASSWORD)
        self.service.at = 1
        self.service.measure = 2
        self.service.register_count = 1
        self.service.auth_count = 1
        self.service.auth_false_count = 5

        self.service.reset()
        self.assertEqual(len(self.service.strategy), 0)
        self.assertEqual(self.service.at, 0)
        self.assertEqual(self.service.measure, 0)
        self.assertEqual(self.service.register_count, 0)
        self.assertEqual(self.service.auth_count, 0)
        self.assertEqual(self.service.auth_false_count, 0)

    def test_display_details_register(self):
        self.service.add(Method.PASSWORD)
        self.service.data_service.get_simulation_details = MagicMock(return_value={"registration": {"register_key": "value"}, "authentication": {"authenticate_key": "value"}})
        self.service.all_registered = MagicMock(return_value=False)
        
        details = self.service.get_display_details()

        self.assertIn("register_key", details)
        self.assertNotIn("authenticate_key", details)
        self.service.data_service.get_simulation_details.assert_called_once_with("password")

    def test_display_details_authenticate(self):
        self.service.add(Method.PASSWORD)
        self.service.data_service.get_simulation_details = MagicMock(return_value={"registration": {"register_key": "value"}, "authentication": {"authenticate_key": "value"}})
        self.service.all_registered = MagicMock(return_value=True)

        details = self.service.get_display_details()
        
        self.assertNotIn("register_key", details)
        self.assertIn("authenticate_key", details)
        self.service.data_service.get_simulation_details.assert_called_once_with("password")

    def test_complete_simulation_badge_one_fa(self):
        self.service.measure = 1
        self.service.complete_simulation()
        self.data_service.update_user_badge.assert_called_once_with(Badge.ONE_FA)
        self.data_service.update_user_simulation.assert_called_once()

    def test_complete_simulation_badge_two_fa(self):
        self.service.measure = 2
        self.service.complete_simulation()
        self.data_service.update_user_badge.assert_called_once_with(Badge.TWO_FA)
        self.data_service.update_user_simulation.assert_called_once()

    def test_complete_simulation_badge_mfa(self):
        self.service.measure = 3
        self.service.complete_simulation()
        self.data_service.update_user_badge.assert_called_once_with(Badge.MFA)
        self.data_service.update_user_simulation.assert_called_once()

    def test_complete_simulation_none(self):
        # Set measure to 0
        self.service.measure = 0
        # Call complete_simulation
        self.service.complete_simulation()
        # Assert that update_user_badge and update_user_simulation were not called
        self.data_service.update_user_badge.assert_not_called()
        self.data_service.update_user_simulation.assert_called_once()

    def test_bypass_success(self):
        # Mock the necessary methods
        self.service.all_authenticated = MagicMock(return_value=False)
        self.service.data_service.update_user_coin = MagicMock(return_value=True)
        self.service.strategy.bypass = MagicMock()

        # Call the bypass method
        result = self.service.bypass()

        # Assertions
        self.assertTrue(result)
        self.service.data_service.update_user_coin.assert_called_once_with(-100)
        self.service.strategy.bypass.assert_called_once_with(0)
        self.assertEqual(self.service.at, 0)
        self.assertEqual(self.service.auth_count, 1)

    def test_bypass_failure_complete(self):
        # Mock the necessary methods
        self.service.all_authenticated = MagicMock(return_value=True)

        # Call the bypass method
        result = self.service.bypass()

        # Assertions
        self.assertFalse(result)

    def test_bypass_failure_coin(self):
        # Mock the necessary methods
        self.service.all_authenticated = MagicMock(return_value=False)
        self.service.data_service.update_user_coin = MagicMock(return_value=False)

        # Call the bypass method
        result = self.service.bypass()

        # Assertions
        self.assertFalse(result)

    def test_session_store(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.SECRET_QUESTION)
        # Define sample data
        sample_data = {"key": "value"}
        self.service.strategy.store = MagicMock()

        # Call session_store method
        self.service.session_store(sample_data)

        # Verify if data is stored
        self.service.strategy.store.assert_called_once_with(0, sample_data)

        self.service.strategy.store.reset_mock()
        self.service.at = 1
        self.service.session_store(sample_data)
        self.service.strategy.store.assert_called_once_with(1, sample_data)


    def test_get_session_stored(self):
        self.service.add(Method.PASSWORD)
        self.service.add(Method.SECRET_QUESTION)
        # Define sample stored data
        stored_data = {"stored_key": "stored_value"}
        stored_data_2 = {"stored_key_2": "stored_value_2"}

        # Mock the get_stored method
        self.service.strategy.get_stored = MagicMock(return_value=stored_data)

        # Call get_session_stored method
        result = self.service.get_session_stored()

        # Assertions
        self.assertEqual(result, stored_data)
        self.service.strategy.get_stored.assert_called_once_with(0)

        self.service.at = 1
        # Mock the get_stored method
        self.service.strategy.get_stored = MagicMock(return_value=stored_data_2)

        # Call get_session_stored method
        result = self.service.get_session_stored()

        # Assertions
        self.assertEqual(result, stored_data_2)
        self.service.strategy.get_stored.assert_called_once_with(1)
  
