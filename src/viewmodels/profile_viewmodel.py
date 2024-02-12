from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QButtonGroup, QLabel
from services.container import ApplicationContainer
from data.data_service import DataService

# pyright: reportAttributeAccessIssue=false

class ProfileViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/profile_view.ui", self)
        self.data_service = ApplicationContainer.data_service()
        self.message_service = ApplicationContainer.message_service()

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.award_btn)
        self.button_group.addButton(self.improvement_btn)
        self.button_group.addButton(self.reading_btn)

        self.coin_count.setText(str(self.data_service.user.get_coins()))
        self.quiz_count.setText(str(self.data_service.user.get_quiz_completed()))
        self.simulation_count.setText(str(self.data_service.user.get_simulation_played()))
        self.set_activites()
        self.message_service.subscribe(self, DataService, self.on_message)

        self.award_btn.clicked.connect(self.buttonClick)
        self.improvement_btn.clicked.connect(self.buttonClick)
        self.reading_btn.clicked.connect(self.buttonClick)

    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Update coins":
            self.coin_count.setText(str(args[0]))
        elif message_title == "Update quiz":
            self.quiz_count.setText(str(args[0]))
        elif message_title == "Update simulation":
            self.simulation_count.setText(str(args[0]))

    def set_activites(self) -> None:
        layout = self.activity_widget.layout()
        activities = self.data_service.user.get_recent_activities()[::-1]

        for activity in activities:
            layout.addWidget(QLabel(activity[2]))
            layout.addWidget(QLabel(activity[1]))
            layout.addWidget(QLabel(activity[3]))

    def buttonClick(self) -> None:
        # GET BUTTON CLICKED
        btn_name = self.sender().objectName()

        match(btn_name):
            case "award_btn":
                self.stackedWidget.setCurrentWidget(self.award_page)
            case "improvement_btn":
                self.stackedWidget.setCurrentWidget(self.improvement_page)
            case "reading_btn":
                self.stackedWidget.setCurrentWidget(self.reading_page)
            case _:
                Exception("Undefined Button Behaviour")

        