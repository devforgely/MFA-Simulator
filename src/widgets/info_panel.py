from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from widgets.list_widgets import ToggleListItem
from widgets.clickables import ClickableLabel
from widgets.dialog import DetailViewDialog
from services.container import ApplicationContainer
from enum import Enum

# pyright: reportAttributeAccessIssue=false

class InfoMode(Enum):
    REGISTER = 0
    AUTHENTICATE = 1
    DEFAULT = 2
    EXPAND = 3

class InfoPanel(QWidget):
    def __init__(self, mode: InfoMode, parent=None) -> None:
        QWidget.__init__(self, parent)
        self.message_service = ApplicationContainer.message_service()

        self.dialog_parent = parent
        self.mode = mode

        if mode == InfoMode.REGISTER:
            uic.loadUi("views_ui/component_views/register_info_view.ui", self)
        elif mode == InfoMode.AUTHENTICATE:
            uic.loadUi("views_ui/component_views/authenticate_info_view.ui", self)
    
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        shadow_effect.setOffset(2, 2)
        shadow_effect.setBlurRadius(50)
        self.setGraphicsEffect(shadow_effect)

    def add_authenticator_description(self, text: str) -> None:
        self.about_description.setText(text)

    def add_advantages(self, advantages: dict[str, str]) -> None:
        if self.mode == InfoMode.REGISTER:  
            for title, description in advantages.items():
                widget = ToggleListItem(title, description, True, self)
                self.advantage_list.layout().addWidget(widget)

    def add_disadvantages(self, disadvantages: dict[str, str]) -> None:
        if self.mode == InfoMode.REGISTER:
            for title, description in disadvantages.items():
                widget = ToggleListItem(title, description, False, self)
                self.disadvantage_list.layout().addWidget(widget)

    def add_about(self, usability: dict[str, str]) -> None:
        if self.mode == InfoMode.AUTHENTICATE:
            layout = self.usability_form.layout()
            score = 0

            for title, rating in usability.items():
                widget = QWidget()
                widget.setStyleSheet("border-bottom: 1px solid #1b232f; font-weight: bold;")
                widget_layout = QHBoxLayout(widget)
                
                title_label = QLabel(title)
                rating_label = QLabel(rating)
                size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
                rating_label.setSizePolicy(size_policy)
                rating_label.setFixedWidth(90)
                rating_label.setAlignment(Qt.AlignCenter)

                if rating == "YES":
                    score += 20
                    rating_label.setStyleSheet("border: 2px solid #6cd577; color: #6cd577;")
                elif rating == "Quasi-YES":
                    score += 10
                    rating_label.setStyleSheet("border: 2px solid #94d56c; color: #94d56c;")
                else:
                    rating_label.setStyleSheet("border: 2px solid #d5786c; color: #d5786c;")

                widget_layout.addWidget(title_label)
                widget_layout.addWidget(rating_label)
                layout.addWidget(widget)

            self.set_measure_level(score)

    def log_text(self, text: str) -> None:
        self.log_console.appendPlainText(text)

    def update_client_status(self, request: str, timestamp: str) -> None:
        self.request_status.setText(request)
        self.timestamp_status.setText(timestamp)

    def update_server_status(self, status: str, status_code: str, response: str) -> None:
        self.server_status_message.setText(status)
        self.server_status_code.setText(status_code)
        self.response_status.setText(response)

    def add_client_data(self, property: str, value: Any, type: InfoMode = InfoMode.DEFAULT) -> None:
        row = self.client_data_layout.rowCount()
        property_title = QLabel(property)
        property_title.setStyleSheet("max-width: 220px;")
        self.client_data_layout.addWidget(property_title, row, 0)

        property_value = None
        property = property.replace(" ", "_")

        if type == InfoMode.DEFAULT:
            property_value = QLabel(value)
            property_value.setObjectName(property)
            self.client_data_layout.addWidget(property_value, row, 1)
        elif type == InfoMode.EXPAND:
            value_container = QWidget()
            value_container.setObjectName(property)
            layout = QHBoxLayout(value_container)
            layout.setContentsMargins(0, 0, 0, 0)

            property_value = ClickableLabel("Click to View")
            property_value.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            property_value.setCursor(Qt.PointingHandCursor)
            property_value.setStyleSheet("""
                                         ClickableLabel { font-weight: bold; background-color: #ed9d35; border-radius: 13%; padding: 3px 7px; }
                                         ClickableLabel:hover { background-color: #d48c2e; }
                                        """)
            property_value.clicked.connect(lambda: self.show_detail_view(value[0], value[1]))
            
            layout.addWidget(property_value, alignment=Qt.AlignLeft)
            self.client_data_layout.addWidget(value_container, row, 1)
        

    def add_server_data(self, property: str, value: Any, type: InfoMode = InfoMode.DEFAULT) -> None:
        row = self.server_data_layout.rowCount()
        property_title = QLabel(property)
        property_title.setStyleSheet("max-width: 220px;")
        self.server_data_layout.addWidget(property_title, row, 0)
        
        property_value = None
        property = property.replace(" ", "_")

        if type == InfoMode.DEFAULT:
            property_value = QLabel(value)
            property_value.setObjectName(property)
            self.server_data_layout.addWidget(property_value, row, 1)
        elif type == InfoMode.EXPAND:
            value_container = QWidget()
            value_container.setObjectName(property)
            layout = QHBoxLayout(value_container)
            layout.setContentsMargins(0, 0, 0, 0)

            property_value = ClickableLabel("Click to View")
            property_value.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            property_value.setCursor(Qt.PointingHandCursor)
            property_value.setStyleSheet("""
                                         ClickableLabel { font-weight: bold; background-color: #ed9d35; border-radius: 13%; padding: 3px 7px; }
                                         ClickableLabel:hover { background-color: #d48c2e; }
                                        """)
            property_value.clicked.connect(lambda: self.show_detail_view(value[0], value[1]))
            
            layout.addWidget(property_value, alignment=Qt.AlignLeft)
            self.server_data_layout.addWidget(value_container, row, 1)
        
    
    def update_client_data(self, property: str, value: Any) -> None:
        property = property.replace(" ", "_")
        for i in range(self.client_data_layout.rowCount()):
            item = self.client_data_layout.itemAtPosition(i, 1)
            if item:
                widget = item.widget()
                if widget is not None and widget.objectName() == property:
                    if isinstance(widget, QLabel) and not isinstance(value, tuple):
                        widget.setText(value)
                    else:
                        clickable_label = widget.layout().itemAt(0).widget()
                        clickable_label.disconnect()
                        clickable_label.clicked.connect(lambda: self.show_detail_view(value[0], value[1]))
                    break

    def update_server_data(self, property: str, value: Any) -> None:
        property = property.replace(" ", "_")
        for i in range(self.server_data_layout.rowCount()):
            item = self.server_data_layout.itemAtPosition(i, 1)
            if item:
                widget = item.widget()
                if widget is not None and widget.objectName() == property:
                    if isinstance(widget, QLabel) and not isinstance(value, tuple):
                        widget.setText(value)
                    else:
                        clickable_label = widget.layout().itemAt(0).widget()
                        clickable_label.disconnect()
                        clickable_label.clicked.connect(lambda: self.show_detail_view(value[0], value[1]))
                    break
    
    def set_measure_level(self, val: int) -> None:
        if val <= 30:
            self.measure_bar.setStyleSheet("#measure_bar::chunk { background-color: #f44336; }")
        elif val <= 50:
            self.measure_bar.setStyleSheet("#measure_bar::chunk { background-color: #ffcd27; }")
        else:
            self.measure_bar.setStyleSheet("#measure_bar::chunk { background-color: #6bcf6f; }")

        self.measure_bar.setValue(val)

    def update_method_note(self, note: str) -> None:
        self.data_note.setText(note)

    def show_detail_view(self, title: str, content: str) -> None:
        self.detail_dialog = DetailViewDialog(title, content, self.dialog_parent)
        self.detail_dialog.move(0, 0)
        self.detail_dialog.show()

            