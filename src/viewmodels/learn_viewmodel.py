from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from services.container import ApplicationContainer
from widgets.markdown_viewer import MarkdownViewer

# pyright: reportGeneralTypeIssues=false

class LearnViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/learn_view.ui", self)
        self.data_service = ApplicationContainer.data_service()

        self.populate_list()
        self.note_container.layout().addWidget(MarkdownViewer())

        self.listWidget.itemClicked.connect(self.display_note_content)
        self.listWidget.itemSelectionChanged.connect(self.change_icon_and_text)

    def populate_list(self):
        for note in self.data_service.get_notes():
            item = QListWidgetItem()
            widget = QWidget()

            icon_label = QLabel()
            icon_label.setPixmap(QPixmap("resources/icons/book.svg"))
            icon_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            text_label = QLabel(note.title)
            text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f;")
            text_label.setAlignment(Qt.AlignLeft)
            icon_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            layout = QHBoxLayout()
            layout.addWidget(icon_label)
            layout.addWidget(text_label)
            widget.setLayout(layout)
            widget.setCursor(Qt.PointingHandCursor)

            item.setSizeHint(widget.sizeHint())

            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def display_note_content(self, item):
        for note in self.data_service.get_notes():
            if note.title == self.listWidget.itemWidget(item).layout().itemAt(1).widget().text():
                self.note_container.layout().itemAt(0).widget().view(note.content)
                break

    def change_icon_and_text(self):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            widget = self.listWidget.itemWidget(item)
            icon_label = widget.layout().itemAt(0).widget()
            text_label = widget.layout().itemAt(1).widget()
            if not item.isSelected():
                icon_label.setPixmap(QPixmap("resources/icons/book.svg"))
                text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f;")
            else:
                icon_label.setPixmap(QPixmap("resources/icons/book-open.svg"))
                text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f; font-weight: bold;")