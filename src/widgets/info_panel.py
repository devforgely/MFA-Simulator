from PyQt5.QtWidgets import QWidget, QTreeWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import Qt

# pyright: reportGeneralTypeIssues=false

class InfoPanel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/component_views/info_view.ui", self)

    def log_text(self, text: str) -> None:
        self.log_console.appendPlainText(text)

    def add_client_status(self, property: str, value: str) -> None:
        item = QTreeWidgetItem([property, value])
        self.client_status_tree.addTopLevelItem(item)
    
    def add_server_status(self, property: str, value: str) -> None:
        item = QTreeWidgetItem([property, value])
        self.server_status_tree.addTopLevelItem(item)

    def add_client_data(self, property: str, value: str) -> None:
        item = QTreeWidgetItem([property, value])
        self.client_data_tree.addTopLevelItem(item)

    def add_server_data(self, property: str, value: str) -> None:
        item = QTreeWidgetItem([property, value])
        self.server_data_tree.addTopLevelItem(item)

    def update_client_status(self, property: str, value: str) -> None:
        items = self.client_status_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            item.setText(1, value)

    def update_server_status(self, property: str, value: str) -> None:
        items = self.server_status_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            item.setText(1, value)
    
    def update_client_data(self, property: str, value: str) -> None:
        items = self.client_data_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            item.setText(1, value)

    def update_server_data(self, property: str, value: str) -> None:
        items = self.server_data_tree.findItems(property, Qt.MatchExactly, 0)

        # Check if the item was found
        if items:
            item = items[0]
            item.setText(1, value)