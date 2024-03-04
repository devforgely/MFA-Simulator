from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer


class LearnViewModel(QObject):
    notes_changed = pyqtSignal(list)
    note_content_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self.data_service = ApplicationContainer.data_service()

    def notes(self) -> None:
        self.notes_changed.emit(self.data_service.get_notes())

    def note_content(self, index) -> None:
        self.note_content_changed.emit(self.data_service.read_note_content(index))