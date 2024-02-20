from dependency_injector import containers, providers
from data.data_service import DataService
from services.authentication_service import AuthenticationService
from services.quiz_service import QuizService
from services.message_service import MessageService

class ApplicationContainer(containers.DeclarativeContainer):
    message_service = providers.Singleton(MessageService)
    data_service = providers.Singleton(
        DataService,
        message_service=message_service)
    authentication_service = providers.Singleton(
        AuthenticationService,
        data_service=data_service
    )
    quiz_service = providers.Singleton(
        QuizService,
        data_service=data_service
    )

    @classmethod
    def get_service_count(cls):
        return len(cls.__dict__)
    