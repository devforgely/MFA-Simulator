from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer


class ManageViewModel(QObject):
    start_up_changed = pyqtSignal(int)
    quiz_expand_changed = pyqtSignal(bool)
    notification_toggle_changed = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        
        self.data_service = ApplicationContainer.data_service()
    
    def start_up_index(self) -> None:
        self.start_up_changed.emit(self.data_service.get_system_start_up())

    def quiz_expand_toggle(self) -> None:
        self.quiz_expand_changed.emit(self.data_service.get_custom_quiz_setting_expand())

    def notification_toggle(self) -> None:
        self.notification_toggle_changed.emit(self.data_service.is_system_show_notification())

    def change_start_up_index(self, i: int) -> None:
        self.data_service.change_system_start_up(i)

    def change_quiz_expand(self, state: bool) -> None:
        self.data_service.change_custom_quiz_setting_expand(state)

    def change_notification_state(self, state: bool) -> None:
        self.data_service.set_system_show_notification(state)

    def reset_application(self) -> None:
        self.data_service.reset_data()
