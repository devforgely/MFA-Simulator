from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem
from services.container import ApplicationContainer


class LearnViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/learn_view.ui", self)
        self.data_service = ApplicationContainer.data_service()

        self.populate_list()
        self.listWidget.itemClicked.connect(self.display_note_content)

    def populate_list(self):
        for note in self.data_service.get_notes():
            item = QListWidgetItem(note.title)
            self.listWidget.addItem(item)

    def display_note_content(self, item):
        for note in self.data_service.get_notes():
            if note.title == item.text():
                self.note_content.setText(note.content)
                break