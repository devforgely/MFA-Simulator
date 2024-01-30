from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from services.container import ApplicationContainer

# pyright: reportGeneralTypeIssues=false

class LearnViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/learn_view.ui", self)
        self.data_service = ApplicationContainer.data_service()

        self.populate_list()

        self.listWidget.itemSelectionChanged.connect(self.change_icon_and_text)
        self.expand_btn.clicked.connect(self.expand_collapse_panel)
        self.up_page_btn.clicked.connect(self.select_previous_item)
        self.down_page_btn.clicked.connect(self.select_next_item)

        self.listWidget.setCurrentRow(0)

    def populate_list(self) -> None:
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

    def display_note_content(self, index) -> None:
        self.note.view(self.data_service.read_note(index).content)

    def change_icon_and_text(self) -> None:
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
                self.display_note_content(i)
                
                icon_label.setPixmap(QPixmap("resources/icons/book-open.svg"))
                text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f; font-weight: bold;")

                if i == 0:
                    self.up_page_btn.setIcon(QIcon("resources/icons/chevron-up-light.svg"))
                    self.up_page_btn.setEnabled(False)
                else:
                    self.up_page_btn.setIcon(QIcon("resources/icons/chevron-up.svg"))
                    self.up_page_btn.setEnabled(True)

                if i == self.listWidget.count()-1:
                    self.down_page_btn.setIcon(QIcon("resources/icons/chevron-down-light.svg"))
                    self.down_page_btn.setEnabled(False)
                else:              
                    self.down_page_btn.setIcon(QIcon("resources/icons/chevron-down.svg"))
                    self.down_page_btn.setEnabled(True)
    
    def expand_collapse_panel(self) -> None:
        self.menu.toggle()
        if self.menu.is_expanded:
            self.expand_btn.setIcon(QIcon("resources/icons/expand-arrow.svg"))
            self.expand_btn.setIconSize(QSize(18, 18))
            self.horizontalWidget.setStyleSheet("border-left: 1px solid silver;")
            self.note_container.setStyleSheet("border-left: 1px solid silver;")
        else:
            self.expand_btn.setIcon(QIcon("resources/icons/chevrons-right.svg"))
            self.expand_btn.setIconSize(QSize(28, 28))
            self.horizontalWidget.setStyleSheet("border-left: none;")
            self.note_container.setStyleSheet("border-left: none;")


    def select_next_item(self):
        current_index = self.listWidget.currentRow()
        if current_index < self.listWidget.count() - 1:  # Check if it's not the last item
            self.listWidget.setCurrentRow(current_index + 1)

    def select_previous_item(self):
        current_index = self.listWidget.currentRow()
        if current_index > 0:  # Check if it's not the first item
            self.listWidget.setCurrentRow(current_index - 1)  