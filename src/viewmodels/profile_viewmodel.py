from typing import Any
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QButtonGroup, QLabel, QVBoxLayout,QListWidgetItem, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QPixmap
from services.container import ApplicationContainer
from data.data_service import DataService
from configuration.app_configuration import Settings

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

        self.coin_count.setText(str(self.data_service.get_user_coins()))
        self.quiz_count.setText(str(self.data_service.get_user_quiz_completed()))
        self.simulation_count.setText(str(self.data_service.get_user_simulation_played()))
        self.update_activites()
        self.update_badges()
        self.update_improvements()
        self.message_service.subscribe(self, DataService, self.on_message)

        self.award_btn.clicked.connect(self.button_click)
        self.improvement_btn.clicked.connect(self.button_click)
        self.reading_btn.clicked.connect(self.button_click)

    def on_message(self, message_title: str, *args: Any) -> None:
        match message_title:
            case "Update Coins":
                self.coin_count.setText(str(args[0]))
            case "Update Quiz":
                self.quiz_count.setText(str(args[0]))
                self.update_activites()
            case "Update Simulation":
                self.simulation_count.setText(str(args[0]))
                self.update_activites()
            case "Update Improvements":
                self.update_improvements()
            case "Update Badges":
                self.update_badges()

    def update_activites(self) -> None:
        activities = self.data_service.get_user_recent_activiies()

        for i in reversed(range(self.activity_container.count())): 
            item = self.activity_container.takeAt(i)
            if item.widget() is not None:
                item.widget().deleteLater()

        for index, activity in enumerate(activities):
            activity_widget = QWidget()
            if index != len(activities) - 1:
                activity_widget.setStyleSheet("padding-bottom: 10px; border-bottom: 1px solid gray;")
            else:
                activity_widget.setStyleSheet("padding-bottom: 10px;")
            
            activity_layout = QVBoxLayout(activity_widget)

            title_label = QLabel(activity[0])
            title_label.setStyleSheet("font-weight: bold; font-size: 9pt;")
            
            time_label = QLabel(activity[1])
            time_label.setStyleSheet("color: #879ab1; font-size: 8pt;")

            description_label = QLabel(activity[2])
            description_label.setStyleSheet("color: #879ab1; font-size: 8pt;")

            activity_layout.addWidget(title_label)
            activity_layout.addWidget(time_label)
            activity_layout.addWidget(description_label)
            self.activity_container.addWidget(activity_widget)

    def update_improvements(self) -> None:
        self.improvement_list.clear()

        improvements = self.data_service.get_user_improvements()
        if len(improvements) == 0:
            widget = QListWidgetItem(self.improvement_list)
            label = QLabel("""🔍 No improvement analysed yet: It appears that the quiz hasn't been completed or you have improved your weakness.\nOnce you finish more quiz, area of improvement will be assessed. Keep going! 🌟""")
            label.setWordWrap(True)
            widget.setSizeHint(label.sizeHint())
            self.improvement_list.addItem(widget)
            self.improvement_list.setItemWidget(widget, label)
        else: 
            for category, val in improvements:
                widget = QListWidgetItem(category, self.improvement_list)
                self.improvement_list.addItem(widget)

                val *= -1 #convert to positive
                icon_holder = QWidget()
                hlayout = QHBoxLayout(icon_holder)
                counter = 0
                while val > 0 and counter < 15:
                    icon = QLabel()
                    icon.setToolTip(f"{min(val, 10)} Incorrect")
                    icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH+'x-square.svg'))
                    hlayout.addWidget(icon)
                    val -= 10
                    counter += 1
                if val > 0:
                    icon = QLabel()
                    icon.setToolTip(f"{val} Incorrect")
                    icon.setPixmap(QPixmap(Settings.ICON_FILE_PATH+'x-square.svg'))
                    hlayout.addWidget(icon)

                hlayout.addStretch()
                widget = QListWidgetItem(self.improvement_list)
                widget.setSizeHint(icon_holder.sizeHint())
                self.improvement_list.addItem(widget)
                self.improvement_list.setItemWidget(widget, icon_holder)
    
    def update_badges(self) -> None:
        layout = self.award_page.layout()
        badges = self.data_service.get_user_badges()
        for badge in badges:
            i = badge[0] // layout.columnCount()
            j = badge[0] % layout.columnCount()
            item = layout.itemAtPosition(i, j)
            if item:
                label = item.widget()
                if label:
                    label.setPixmap(QPixmap(Settings.IMAGE_FILE_PATH + badge[1]))

    def display_readings(self) -> None:
        readings = self.data_service.get_user_readings()
        for i in range(len(readings)):
            book_title, has_read = readings[i]
            read_checkbox = QCheckBox(book_title)
            read_checkbox.setChecked(has_read)
            read_checkbox.stateChanged.connect(lambda state, title=book_title, pos=i: self.checkbox_changed(state, title, pos))
            self.reading_layout.addWidget(read_checkbox, i // 2, i % 2)
    
    def checkbox_changed(self, state, title, i) -> None:
        self.data_service.update_user_reading(state, title, i)

    def button_click(self) -> None:
        # GET BUTTON CLICKED
        btn_name = self.sender().objectName()

        match(btn_name):
            case "award_btn":
                self.stackedWidget.setCurrentWidget(self.award_page)
            case "improvement_btn":
                self.stackedWidget.setCurrentWidget(self.improvement_page)
            case "reading_btn":
                self.display_readings()
                self.stackedWidget.setCurrentWidget(self.reading_page)
            case _:
                Exception("Undefined Button Behaviour")

        