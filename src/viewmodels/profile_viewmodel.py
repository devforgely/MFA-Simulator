from typing import Any
from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer
from services.data_service import DataService


# pyright: reportAttributeAccessIssue=false

class ProfileViewModel(QObject):
    coin_changed = pyqtSignal(str)
    quiz_amount_changed = pyqtSignal(str)
    simulation_amount_changed = pyqtSignal(str)
    acitivites_changed = pyqtSignal(list)
    badges_changed = pyqtSignal(list)
    improvements_changed = pyqtSignal(list)
    readings_changed = pyqtSignal(list)

    def __init__(self) -> None:
        super().__init__()

        self.data_service = ApplicationContainer.data_service()
        self.message_service = ApplicationContainer.message_service()

        self.message_service.subscribe(self, DataService, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        match message_title:
            case "Update Coins":
                self.coin_changed.emit(str(args[0]))
            case "Update Quiz":
                self.quiz_amount_changed.emit(str(args[0]))
                self.acitivites()
            case "Update Simulation":
                self.simulation_amount_changed.emit(str(args[0]))
                self.acitivites()
            case "Update Improvements":
                self.improvements()
            case "Update Badges":
                self.badges()

    def coin(self) -> None:
        self.coin_changed.emit(str(self.data_service.get_user_coins()))

    def quiz_amount(self) -> None:
        self.quiz_amount_changed.emit(str(self.data_service.get_user_quiz_completed()))

    def simulation_amount(self) -> None:
        self.simulation_amount_changed.emit(str(self.data_service.get_user_simulation_played()))

    def acitivites(self) -> None:
        self.acitivites_changed.emit(self.data_service.get_user_recent_activiies())

    def badges(self) -> None:
        self.badges_changed.emit(self.data_service.get_user_badges())

    def improvements(self) -> None:
        self.improvements_changed.emit(self.data_service.get_user_improvements())

    def readings(self) -> None:
        readings = self.data_service.get_user_readings()
        for i in range(len(readings)):
            book_title, has_read = readings[i]
            if '&' in book_title:
                readings[i] = (book_title.replace("&", "&&"), has_read)
        self.readings_changed.emit(readings)

    def update_reading(self, title: str, state: bool, pos: int) -> None:
        self.data_service.update_user_reading(title, state, pos)
    

        