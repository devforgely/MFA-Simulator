import unittest
from unittest.mock import Mock
from models.authentication.authentication import AuthenticationStrategy, CompoundAuthentication
from models.authentication.authentication_methods import SaltStrategy


class TestCompoundStrategy(unittest.TestCase):
    def setUp(self):
        self.compound_auth = CompoundAuthentication()
        self.mock_strategy_1 = Mock(spec=AuthenticationStrategy)
        self.mock_strategy_2 = Mock(spec=AuthenticationStrategy)
        self.compound_auth.add(self.mock_strategy_1)
        self.compound_auth.add(self.mock_strategy_2)

    def test_init(self):
        self.assertEqual(len(self.compound_auth), 2)

    def test_get_type(self):
        self.assertEqual(self.compound_auth.get_type(0), self.mock_strategy_1.get_type())
        self.assertEqual(self.compound_auth.get_type(1), self.mock_strategy_2.get_type())

    def test_get_all_types(self):
        expected_types = [self.mock_strategy_1.get_type(), self.mock_strategy_2.get_type()]
        self.assertEqual(self.compound_auth.get_all_types(), expected_types)

    def test_add(self):
        new_mock_strategy = Mock(spec=AuthenticationStrategy)
        self.compound_auth.add(new_mock_strategy)
        self.assertEqual(len(self.compound_auth), 3)

    def test_remove(self):
        self.compound_auth.remove(0)
        self.assertEqual(len(self.compound_auth), 1)
        self.assertEqual(self.compound_auth.get_type(0), self.mock_strategy_2.get_type())

    def test_register(self):
        self.mock_strategy_1.register.return_value = True
        result = self.compound_auth.register(0, "data")
        self.assertTrue(result)
        self.mock_strategy_1.register.assert_called_once_with("data")

    def test_authenticate(self):
        self.mock_strategy_2.authenticate.return_value = True
        result = self.compound_auth.authenticate(1, "data")
        self.assertTrue(result)
        self.mock_strategy_2.authenticate.assert_called_once_with("data")

    def test_bypass(self):
        self.compound_auth.bypass(0)
        self.mock_strategy_1.bypass.assert_called_once()

    def test_store(self):
        self.compound_auth.store(0, {"key": "value"})
        self.mock_strategy_1.store.assert_called_once_with({"key": "value"})

    def test_get_stored(self):
        self.mock_strategy_2.get_stored.return_value = {"key": "value"}
        stored_data = self.compound_auth.get_stored(1)
        self.assertEqual(stored_data, {"key": "value"})
        self.mock_strategy_2.get_stored.assert_called_once()


class TestSaltStrategy(unittest.TestCase):
    def setUp(self):
        self.salt_strategy = SaltStrategy()

    def test_hash_secret(self):
        # Arrange
        secret = "password"
        salt = self.salt_strategy.generate_salt()

        # Act
        hashed_secret = self.salt_strategy.hash_secret(secret, salt)

        # Assert
        self.assertTrue(hashed_secret)

    def test_generate_salt(self):
        # Act
        salt = self.salt_strategy.generate_salt()

        # Assert
        self.assertTrue(salt)
        self.assertEqual(len(salt), 16)  # By default, the length should be 16 bytes

    def test_generate_salt_custom_length(self):
        # Arrange
        custom_length = 32

        # Act
        salt = self.salt_strategy.generate_salt(length=custom_length)

        # Assert
        self.assertTrue(salt)
        self.assertEqual(len(salt), custom_length)

    def test_hash_different_secret(self):
        # Arrange
        secret_1 = "password"
        secret_2 = "passw0ord"
        salt = self.salt_strategy.generate_salt()

        # Act
        hashed_secret_1 = self.salt_strategy.hash_secret(secret_1, salt)
        hashed_secret_2 = self.salt_strategy.hash_secret(secret_2, salt)

        # Assert
        self.assertNotEqual(hashed_secret_1, hashed_secret_2)
