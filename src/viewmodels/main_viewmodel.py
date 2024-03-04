from typing import Any
from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer
from data.data_service import DataService
from viewmodels.simulate_viewmodels import SimulateViewModel, CreatorViewModel
from viewmodels.quiz_viewmodels import QuizViewModel
from viewmodels.learn_viewmodel import LearnViewModel
from viewmodels.profile_viewmodel import ProfileViewModel
from viewmodels.manage_viewmodel import ManageViewModel
from PyQt5.QtGui import QIcon
from configuration.app_configuration import Settings


class MainViewModel(QObject):
    fact_changed = pyqtSignal(str)
    coin_count_changed = pyqtSignal(str)
    badge_count_changed = pyqtSignal(str)
    info_bar_added = pyqtSignal(QIcon, str)

    def __init__(self) -> None:
        super().__init__()
        
        self.data_service = ApplicationContainer.data_service()
        self.message_service = ApplicationContainer.message_service()

        self.is_show_notification = self.data_service.is_system_show_notification()
        
        self.message_service.subscribe(self, DataService, self.on_message)
        self.message_service.subscribe(self, CreatorViewModel, self.on_message)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Update Coins":
            self.coin_count_changed.emit(str(args[0]))
            if args[1]: # bool to determine whether if you have earned coins or not
                self.add_info_bar(QIcon(Settings.IMAGE_FILE_PATH+"coin.png"), "success", "You've just earned some coins!")
        elif message_title == "Insufficient Coins":
            self.add_info_bar(QIcon(Settings.IMAGE_FILE_PATH+"coin.png"), "warning", f"Requires {args[0]} more coins.")
        elif message_title == "Update Badges":
            self.badge_count_changed.emit(f"{args[0][0]}/{args[0][1]}")
            self.add_info_bar(QIcon(Settings.IMAGE_FILE_PATH+"star-medal.png"), "success", f"You've been awarded with {args[1]} MFA badge!")
        elif message_title == "Info Notification":
            self.add_info_bar(args[0], "info", args[1])
        elif message_title == "Warning Notification":
            self.add_info_bar(args[0], "warning", args[1])
        elif message_title == "Error Notification":
            self.add_info_bar(args[0], "error", args[1])
        elif message_title == "Update Notification":
            self.is_show_notification = args[0]

        # update fun fact once a while, while being every time when there is new message
        self.fact_changed.emit(self.data_service.get_fun_fact())

    def fact(self) -> None:
        self.fact_changed.emit(self.data_service.get_fun_fact())

    def coin_count(self) -> None:
        self.coin_count_changed.emit(str(self.data_service.get_user_coins()))

    def badge_count(self) -> None:
        earned, total = self.data_service.get_user_badges_count()
        self.badge_count_changed.emit(f"{earned}/{total}")

    def add_info_bar(self, icon, title, description) -> None:
        if self.is_show_notification:
            self.info_bar_added.emit(icon, description)

    def get_system_startup(self) -> int:
        return self.data_service.get_system_start_up()
    
    def help(self) -> None:
        self.message_service.send(self, "Help")