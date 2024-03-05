from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false

class LearnView(QWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/learn_view.ui", self)

        self._viewmodel = viewmodel
        self._viewmodel.notes_changed.connect(self.update_title_list)
        self._viewmodel.note_content_changed.connect(self.note.view)

        self.setup_ui()

        self._viewmodel.notes()
        self._viewmodel.note_content(0)
        self.listWidget.setCurrentRow(0)

    def setup_ui(self) -> None:
        self.listWidget.itemSelectionChanged.connect(self.change_icon_and_text)
        self.expand_btn.clicked.connect(self.expand_collapse_panel)
        self.up_page_btn.clicked.connect(self.select_previous_item)
        self.down_page_btn.clicked.connect(self.select_next_item)

        self.light_theme.clicked.connect(lambda: self.change_theme(0))
        self.light_peach_theme.clicked.connect(lambda: self.change_theme(1))
        self.peach_theme.clicked.connect(lambda: self.change_theme(2))
        self.yellow_theme.clicked.connect(lambda: self.change_theme(3))
        self.orange_theme.clicked.connect(lambda: self.change_theme(4))
        self.dark_theme.clicked.connect(lambda: self.change_theme(5))
        self.change_theme(0)

        self.font_slider.valueChanged.connect(self.font_size_changed)
        self.font_slider.setValue(0)

        self.listWidget.setCurrentRow(0)

    def update_title_list(self, notes: list) -> None:
        for note in notes:
            item = QListWidgetItem()
            widget = QWidget()
            widget.setCursor(Qt.PointingHandCursor)

            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH + "book.svg"))
            icon_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            text_label = QLabel(note.title)
            text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f;")
            text_label.setAlignment(Qt.AlignLeft)
            icon_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            layout = QHBoxLayout(widget)
            layout.addWidget(icon_label)
            layout.addWidget(text_label)

            item.setSizeHint(widget.sizeHint())

            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def change_icon_and_text(self) -> None:
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            widget = self.listWidget.itemWidget(item)
            icon_label = widget.layout().itemAt(0).widget()
            text_label = widget.layout().itemAt(1).widget()
            if not item.isSelected():
                icon_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH + "book.svg"))
                text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f;")
            else:
                self._viewmodel.note_content(i)
                
                icon_label.setPixmap(QPixmap(Settings.ICON_FILE_PATH + "book-open.svg"))
                text_label.setStyleSheet("font-size: 12pt; border: none; border-bottom: 1px solid #37352f; \
                                      padding-bottom: 4px; color: #37352f; font-weight: bold;")

                if i == 0:
                    self.up_page_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "chevron-up-light.svg"))
                    self.up_page_btn.setEnabled(False)
                else:
                    self.up_page_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "chevron-up.svg"))
                    self.up_page_btn.setEnabled(True)

                if i == self.listWidget.count()-1:
                    self.down_page_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "chevron-down-light.svg"))
                    self.down_page_btn.setEnabled(False)
                else:              
                    self.down_page_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "chevron-down.svg"))
                    self.down_page_btn.setEnabled(True)

    def expand_collapse_panel(self) -> None:
        self.menu.toggle()
        if self.menu.is_expanded:
            self.expand_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "expand-arrow.svg"))
            self.expand_btn.setIconSize(QSize(18, 18))
            self.horizontalWidget.setStyleSheet("#horizontalWidget {border-left: 1px solid silver;}")
            self.note_container.setStyleSheet("#note_container {border-left: 1px solid silver;}")
        else:
            self.expand_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "chevrons-right.svg"))
            self.expand_btn.setIconSize(QSize(28, 28))
            self.horizontalWidget.setStyleSheet("#horizontalWidget { border-left: none;}")
            self.note_container.setStyleSheet("#note_container {border-left: none;}")

    def select_next_item(self):
        current_index = self.listWidget.currentRow()
        if current_index < self.listWidget.count() - 1:  # Check if it's not the last item
            self.listWidget.setCurrentRow(current_index + 1)

    def select_previous_item(self):
        current_index = self.listWidget.currentRow()
        if current_index > 0:  # Check if it's not the first item
            self.listWidget.setCurrentRow(current_index - 1)

    def font_size_changed(self, value: int) -> None:
        self.note.adjust_font_size(value)
    
    def change_theme(self, theme: int) -> None:
        self.note.adjust_theme(theme) 

    