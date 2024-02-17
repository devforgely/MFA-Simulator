from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from services.container import ApplicationContainer


class ManageViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/manage_view.ui", self)
        self.data_service = ApplicationContainer.data_service()

        start_up_index = self.data_service.get_system_start_up()
        if start_up_index == 0:
            self.default_location_btn.setChecked(True)
            self.start_up_combobox.setEnabled(False)
        else:
            self.custom_location_btn.setChecked(True)
            self.start_up_combobox.setCurrentIndex(start_up_index)

        self.expand_toggle.setChecked(self.data_service.get_custom_quiz_expand())
        self.change_custom_expand_text(self.expand_toggle.isChecked())

        self.default_location_btn.clicked.connect(self.set_default_location)
        self.custom_location_btn.clicked.connect(lambda: self.start_up_combobox.setEnabled(True))
        self.start_up_combobox.currentIndexChanged.connect(self.on_start_up_changed)

        self.expand_toggle.clicked.connect(lambda state: self.toggle_custom_expand(state))

        self.reset_btn.clicked.connect(self.data_service.reset_data)

    def set_default_location(self) -> None:
        self.data_service.change_system_start_up(0)
        self.start_up_combobox.setEnabled(False)

    def on_start_up_changed(self, index) -> None:
        self.data_service.change_system_start_up(index)

    def change_custom_expand_text(self, state) -> None:
        if state:
            self.custom_quiz_expand.setText("Auto Expand")
        else:
            self.custom_quiz_expand.setText("Auto Collapse")

    def toggle_custom_expand(self, state) -> None:
        self.change_custom_expand_text(state)
        self.data_service.change_custom_quiz_expand(state)