import unittest
from unittest.mock import MagicMock, patch
from services.container import ApplicationContainer
from services.data_service import DataService
from services.authentication_service import AuthenticationService
from services.quiz_service import QuizService
from services.message_service import MessageService

class TestApplicationContainer(unittest.TestCase):
    def test_get_service_count(self):
        # Arrange
        expected_count = 5  # number of services in the container
        
        # Act
        count = ApplicationContainer.get_service_count()

        # Assert
        self.assertEqual(count, expected_count)

    def test_services_dependency_injection(self):
        # Arrange
        message_service_mock = MagicMock(spec=MessageService)
        data_service_mock = MagicMock(spec=DataService)
        authentication_service_mock = MagicMock(spec=AuthenticationService)
        quiz_service_mock = MagicMock(spec=QuizService)
        
        with patch.object(ApplicationContainer, 'message_service', return_value=message_service_mock), \
            patch.object(ApplicationContainer, 'data_service', return_value=data_service_mock), \
            patch.object(ApplicationContainer, 'authentication_service', return_value=authentication_service_mock), \
            patch.object(ApplicationContainer, 'quiz_service', return_value=quiz_service_mock):

            # Act
            message_service = ApplicationContainer.message_service()
            data_service = ApplicationContainer.data_service()
            authentication_service = ApplicationContainer.authentication_service()
            quiz_service = ApplicationContainer.quiz_service()

            # Assert
            self.assertIsInstance(message_service, MessageService)
            self.assertIsInstance(data_service, DataService)
            self.assertIsInstance(authentication_service, AuthenticationService)
            self.assertIsInstance(quiz_service, QuizService)