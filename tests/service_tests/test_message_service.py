import unittest
from unittest.mock import MagicMock
from services.message_service import MessageService
from services.data_service import DataService

class TestMessageService(unittest.TestCase):
    def setUp(self):
        # Create a MessageService instance
        self.message_service = MessageService()

    def test_subscribe(self):
        # Arrange
        subscriber_instance_1 = MagicMock()
        subscriber_instance_2 = MagicMock()
        callback = MagicMock()
        publisher_type = type(MagicMock())

        # Act
        self.message_service.subscribe(subscriber_instance_1, publisher_type, callback)
        self.message_service.subscribe(subscriber_instance_2, publisher_type, callback)

        # Assert
        self.assertIn(publisher_type, self.message_service.subscriptions)
        self.assertEqual(len(self.message_service.subscriptions[publisher_type]), 2)

    def test_unsubscribe(self):
        # Arrange
        subscriber_instance_1 = MagicMock()
        subscriber_instance_2 = MagicMock()
        callback = MagicMock()
        publisher_type = type(MagicMock())
        self.message_service.subscribe(subscriber_instance_1, publisher_type, callback)
        self.message_service.subscribe(subscriber_instance_2, publisher_type, callback)

        # Act
        self.message_service.unsubscribe(subscriber_instance_1)

        # Assert
        self.assertNotIn(type(subscriber_instance_1), self.message_service.subscriptions[publisher_type])
        self.assertEqual(len(self.message_service.subscriptions[publisher_type]), 1)

    def test_send(self):
        # Arrange
        sender = MagicMock()
        subscriber_instance = MagicMock()
        data_instance_type = type(DataService)
        callback = MagicMock()
        callback_data = MagicMock()
        self.message_service.subscribe(subscriber_instance, type(sender), callback)
        self.message_service.subscribe(subscriber_instance, data_instance_type, callback_data)

        # Act
        self.message_service.send(sender, "Test Message", "arg1", "arg2")

        # Assert
        callback.assert_called_once_with("Test Message", "arg1", "arg2")
        callback_data.assert_not_called()

    def test_unsubscribe_all(self):
        # Arrange
        subscriber_instance = MagicMock()
        callback = MagicMock()
        self.message_service.subscribe(subscriber_instance, type(MagicMock()), callback)
        self.assertEqual(len(self.message_service.subscriptions), 1)
        
        # Act
        self.message_service.unsubscribe_all()

        # Assert
        self.assertEqual(len(self.message_service.subscriptions), 0)