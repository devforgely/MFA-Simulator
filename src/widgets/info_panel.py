from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from typing import Any
from widgets.list_widgets import ToggleListItem
from widgets.clickables import ClickableLabel
from services.container import ApplicationContainer

# pyright: reportAttributeAccessIssue=false

class InfoPanel(QWidget):
    def __init__(self, display_details: dict, mode: int) -> None:
        QWidget.__init__(self)
        self.message_service = ApplicationContainer.message_service()

        self.notes = display_details["notes"]
        self.mode = mode

        if mode == 0:
            uic.loadUi("views/component_views/register_info_view.ui", self)
            self.add_advantages(display_details["advantages"])
            self.add_disadvantages(display_details["disadvantages"])
        else:
            uic.loadUi("views/component_views/authenticate_info_view.ui", self)
            self.add_about(display_details["usability"])
        
        self.add_authenticator_description(display_details["description"])
        self.update_data_note(0)
    
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        shadow_effect.setOffset(2, 2)
        shadow_effect.setBlurRadius(50)
        self.setGraphicsEffect(shadow_effect)

    def add_authenticator_description(self, text: str) -> None:
        self.about_description.setText(text)

    def add_advantages(self, advantages: dict[str, str]) -> None:   
        for title, description in advantages.items():
            widget = ToggleListItem(title, description, True, self)
            self.advantage_list.layout().addWidget(widget)

    def add_disadvantages(self, disadvantages: dict[str, str]) -> None:
        for title, description in disadvantages.items():
            widget = ToggleListItem(title, description, False, self)
            self.disadvantage_list.layout().addWidget(widget)

    def add_about(self, usability: dict[str, str]) -> None:
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

    def add_client_data(self, property: str, value: Any, value_type: str = "default") -> None:
        row = self.client_data_layout.rowCount()
        property_title = QLabel(property)
        property_title.setStyleSheet("width: 50%")
        self.client_data_layout.addWidget(property_title, row, 0)

        property_value = None
        property = property.replace(" ", "_")

        if value_type == "default":
            property_value = QLabel(value)
            property_value.setObjectName(property)
        elif value_type == "expand":
            property_value = ClickableLabel("<u>$Click to View$</u>")
            property_value.setObjectName(property)
            property_value.setStyleSheet(f"#{property}:hover {{ color: #0067c0;}}")

            if self.mode == 0:
                property_value.clicked.connect(lambda: self.message_service.send(self, "Register Show Details", value[0], value[1]))
            else:
                property_value.clicked.connect(lambda: self.message_service.send(self, "Authenticate Show Details", value[0], value[1]))
            
        self.client_data_layout.addWidget(property_value, row, 1)

    def add_server_data(self, property: str, value: Any, value_type: str = "default") -> None:
        row = self.server_data_layout.rowCount()
        property_title = QLabel(property)
        property_title.setStyleSheet("width: 50%")
        self.server_data_layout.addWidget(property_title, row, 0)
        
        property_value = None
        property = property.replace(" ", "_")

        if value_type == "default":
            property_value = QLabel(value)
            property_value.setObjectName(property)
        elif value_type == "expand":
            property_value = ClickableLabel("<u>$Click to View$</u>")
            property_value.setObjectName(property)
            property_value.setStyleSheet(f"#{property}:hover {{ color: #0067c0;}}")

            if self.mode == 0:
                property_value.clicked.connect(lambda: self.message_service.send(self, "Register Show Details", value[0], value[1]))
            else:
                property_value.clicked.connect(lambda: self.message_service.send(self, "Authenticate Show Details", value[0], value[1]))
        
        self.server_data_layout.addWidget(property_value, row, 1)
    
    def update_client_data(self, property: str, value: Any, value_type: str = "default") -> None:
        property = property.replace(" ", "_")
        for i in range(self.client_data_layout.rowCount()):
            item = self.client_data_layout.itemAtPosition(i, 1)
            if item:
                widget = item.widget()
                if widget is not None and widget.objectName() == property:
                    if value_type == "default":
                        widget.setText(value)
                    elif value_type == "expand":
                        if self.mode == 0:
                            widget.disconnect()
                            widget.clicked.connect(lambda: self.message_service.send(self, "Register Show Details", value[0], value[1]))
                        else:
                            widget.disconnect()
                            widget.clicked.connect(lambda: self.message_service.send(self, "Authenticate Show Details", value[0], value[1]))
                    break

    def update_server_data(self, property: str, value: Any, value_type: str = "default") -> None:
        property = property.replace(" ", "_")
        for i in range(self.server_data_layout.rowCount()):
            item = self.server_data_layout.itemAtPosition(i, 1)
            if item:
                widget = item.widget()
                if widget is not None and widget.objectName() == property:
                    if value_type == "default":
                        widget.setText(value)
                    elif value_type == "expand":
                        if self.mode == 0:
                            widget.disconnect()
                            widget.clicked.connect(lambda: self.message_service.send(self, "Register Show Details", value[0], value[1]))
                        else:
                            widget.disconnect()
                            widget.clicked.connect(lambda: self.message_service.send(self, "Authenticate Show Details", value[0], value[1]))
                    break
    
    def set_measure_level(self, val: int) -> None:
        if val <= 30:
            self.measure_bar.setStyleSheet("#measure_bar::chunk { background-color: #f44336; }")
        elif val <= 50:
            self.measure_bar.setStyleSheet("#measure_bar::chunk { background-color: #ffcd27; }")
        else:
            self.measure_bar.setStyleSheet("#measure_bar::chunk { background-color: #6bcf6f; }")

        self.measure_bar.setValue(val)

    def update_data_note(self, index: int) -> None:
        self.data_note.setText(self.notes[index])
                    
            