from dependency_injector import containers, providers
from data.data_service import DataService
from services.authentication_service import AuthenticationService
from services.quiz_service import QuizService
from services.message_service import MessageService

class ApplicationContainer(containers.DeclarativeContainer):
    data_service = providers.Singleton(DataService)
    authentication_service = providers.Singleton(
        AuthenticationService,
        data_service=data_service
    )
    quiz_service = providers.Singleton(
        QuizService,
        data_service=data_service
    )
    message_service = providers.Singleton(MessageService)