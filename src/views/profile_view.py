from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QButtonGroup, QLabel, QVBoxLayout,QListWidgetItem, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QPixmap
from configuration.app_configuration import Settings


class ProfileView(QWidget):
    def __init__(self, viewmodel, parent: QWidget, ui="views_ui/profile_view.ui") -> None:
        super().__init__(parent)
        uic.loadUi(ui, self)

        self._viewmodel = viewmodel
        self._viewmodel.coin_changed.connect(self.coin_count.setText)
        self._viewmodel.quiz_amount_changed.connect(self.quiz_count.setText)
        self._viewmodel.simulation_amount_changed.connect(self.simulation_count.setText)
        self._viewmodel.acitivites_changed.connect(self.update_activites)
        self._viewmodel.badges_changed.connect(self.update_badges)
        self._viewmodel.improvements_changed.connect(self.update_improvements)
        self._viewmodel.readings_changed.connect(self.update_readings)

        self.setup_ui()

        self._viewmodel.coin()
        self._viewmodel.quiz_amount()
        self._viewmodel.simulation_amount()
        self._viewmodel.acitivites()
        self._viewmodel.badges()
        self._viewmodel.improvements()
        

    def setup_ui(self) -> None:
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.award_btn)
        self.button_group.addButton(self.improvement_btn)
        self.button_group.addButton(self.reading_btn)

        self.award_btn.clicked.connect(self.button_click)
        self.improvement_btn.clicked.connect(self.button_click)
        self.reading_btn.clicked.connect(self.button_click)

    def update_activites(self, activities: list) -> None:
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

    def update_badges(self, badges: list) -> None:
        layout = self.award_page.layout()
        
        for badge in badges:
            i = badge[0] // layout.columnCount()
            j = badge[0] % layout.columnCount()
            item = layout.itemAtPosition(i, j)
            if item:
                label = item.widget()
                if label:
                    label.setPixmap(QPixmap(Settings.IMAGE_FILE_PATH + badge[1]))

    def update_improvements(self, improvements: list) -> None:
        self.improvement_list.clear()

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

    def update_readings(self, readings: list) -> None:
        for i in range(len(readings)):
            book_title, has_read = readings[i]
            read_checkbox = QCheckBox(book_title)
            read_checkbox.setChecked(has_read)
            read_checkbox.stateChanged.connect(lambda state, title=book_title, pos=i: self._viewmodel.update_reading(title, state, pos))
            self.reading_layout.addWidget(read_checkbox, i // 2, i % 2)    

    def button_click(self) -> None:
        # GET BUTTON CLICKED
        btn_name = self.sender().objectName()

        match(btn_name):
            case "award_btn":
                self.stackedWidget.setCurrentWidget(self.award_page)
            case "improvement_btn":
                self.stackedWidget.setCurrentWidget(self.improvement_page)
            case "reading_btn":
                self._viewmodel.readings()
                self.stackedWidget.setCurrentWidget(self.reading_page)
            case _:
                Exception("Undefined Button Behaviour")