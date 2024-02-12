from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QLabel, QTextEdit, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from typing import Any

# pyright: reportAttributeAccessIssue=false

class InfoPanel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/component_views/info_view.ui", self)

        self.add_client_status("connection", "established")
        self.add_client_status("request", "null")
        self.add_client_status("timestamp", "null")

        self.add_server_status("status", "204")
        self.add_server_status("message", "null")

        self.client_data_tree.setColumnWidth(0, 180)
        self.server_data_tree.setColumnWidth(0, 180)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setBlurRadius(50)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        self.setGraphicsEffect(shadow_effect)


    def log_text(self, text: str) -> None:
        self.log_console.appendPlainText(text)

    def create_label(self, value) -> QLabel:
        label = QLabel(value)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        label.setWordWrap(True)
        label.setFixedHeight(35)
        return label

    def create_scroll_label(self, value) -> QTextEdit:
        text_edit = QTextEdit(value)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("border: none")
        text_edit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        text_edit.setFixedHeight(40)
        return text_edit

    def add_client_status(self, property: str, value: str) -> None:
        item = QTreeWidgetItem([property])
        self.client_status_tree.addTopLevelItem(item)
        self.client_status_tree.setItemWidget(item, 1, self.create_label(value))
    
    def add_server_status(self, property: str, value: str) -> None:
        item = QTreeWidgetItem([property])
        self.server_status_tree.addTopLevelItem(item)
        self.server_status_tree.setItemWidget(item, 1, self.create_label(value))

    def add_client_data(self, property: str, value: Any) -> None:
        item = QTreeWidgetItem([property])

        if isinstance(value, list):
            if value:
                item.setText(1, f"list of {property}")
                for text in value:
                    child = QTreeWidgetItem(item)
                    self.client_data_tree.setItemWidget(child, 1,  self.create_label('\u2022 '+ text))
            else:
                item.setText(1, "empty list")
            self.client_data_tree.addTopLevelItem(item)
        else:
            self.client_data_tree.addTopLevelItem(item)
            self.client_data_tree.setItemWidget(item, 1, self.create_scroll_label(value))

    def add_server_data(self, property: str, value: Any) -> None:
        item = QTreeWidgetItem([property])

        if isinstance(value, list):
            if value:
                item.setText(1, f"list of {property}")
                for text in value:
                    child = QTreeWidgetItem(item)
                    self.server_data_tree.setItemWidget(child, 1, self.create_label('\u2022 '+ text))
            else:
                item.setText(1, "empty list")

            self.server_data_tree.addTopLevelItem(item)
        else:
            self.server_data_tree.addTopLevelItem(item)
            self.server_data_tree.setItemWidget(item, 1, self.create_scroll_label(value))

    def update_client_status(self, property: str, value: str) -> None:
        items = self.client_status_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            label = self.client_status_tree.itemWidget(item, 1)
            if label:
                label.setText(value)

    def update_server_status(self, property: str, value: str) -> None:
        items = self.server_status_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            label = self.server_status_tree.itemWidget(item, 1)
            if label:
                label.setText(value)
    
    def update_client_data(self, property: str, value: Any) -> None:
        items = self.client_data_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            if isinstance(value, list):
                # Remove all existing child items
                while item.childCount() > 0:
                    item.removeChild(item.child(0))
                # Add new child items
                if value:
                    item.setText(1, f"list of {property}")
                    for text in value:
                        child = QTreeWidgetItem(item)
                        self.client_data_tree.setItemWidget(child, 1, self.create_label('\u2022 '+ text))
                else:
                    item.setText(1, f"empty list")
            else:
                label = self.client_data_tree.itemWidget(item, 1)
                if label:
                    label.setText(value)
            

    def update_server_data(self, property: str, value: Any) -> None:
        items = self.server_data_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            if isinstance(value, list):
                # Remove all existing child items
                while item.childCount() > 0:
                    item.removeChild(item.child(0))
                # Add new child items
                if value:
                    item.setText(1, f"list of {property}")
                    for text in value:
                        child = QTreeWidgetItem(item)
                        self.server_data_tree.setItemWidget(child, 1, self.create_label('\u2022 '+ text))
                else:
                    item.setText(1, f"empty list")
            else:
                label = self.server_data_tree.itemWidget(item, 1)
                if label:
                    label.setText(value)
                    
            