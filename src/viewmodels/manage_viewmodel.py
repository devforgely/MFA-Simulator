from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from widgets.dialog import AboutDialog


class ManageViewModel(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        uic.loadUi("views/manage_view.ui", self)
        self.data_service = ApplicationContainer.data_service()

        self.about = None

        self.start_up_combobox.setStyleSheet(f"""
                QComboBox::down-arrow {{
                    image: url({Settings.ICON_FILE_PATH}down-arrow.svg);
                    width: 18px;
                    height: 18px;
                    margin-right: 15px;
                }}
            """)

        sp_retain = self.reset_container.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.reset_container.setSizePolicy(sp_retain)
        self.reset_container.setVisible(False)

        start_up_index = self.data_service.get_system_start_up()
        if start_up_index == 0:
            self.default_location_btn.setChecked(True)
            self.start_up_combobox.setEnabled(False)
        else:
            self.custom_location_btn.setChecked(True)
            self.start_up_combobox.setCurrentIndex(start_up_index)

        self.expand_toggle.setChecked(self.data_service.get_custom_quiz_expand())
        self.notification_toggle.setChecked(self.data_service.is_system_show_notification())

        self.default_location_btn.clicked.connect(self.set_default_location)
        self.custom_location_btn.clicked.connect(lambda: self.start_up_combobox.setEnabled(True))
        self.start_up_combobox.currentIndexChanged.connect(self.on_start_up_changed)

        self.expand_toggle.clicked.connect(lambda state: self.toggle_custom_expand(state))

        self.notification_toggle.clicked.connect(lambda state: self.toggle_notification(state))

        self.about_label.clicked.connect(self.show_about)

        self.toggle_reset_btn.clicked.connect(self.toggle_reset)
        self.reset_btn.clicked.connect(self.reset)

    def set_default_location(self) -> None:
        self.data_service.change_system_start_up(0)
        self.start_up_combobox.setEnabled(False)

    def on_start_up_changed(self, index) -> None:
        self.data_service.change_system_start_up(index)

    def toggle_custom_expand(self, state) -> None:
        self.data_service.change_custom_quiz_expand(state)

    def toggle_notification(self, state) -> None:
        self.data_service.set_system_show_notification(state)

    def toggle_reset(self) -> None:
        if self.reset_container.isVisible():
            self.reset_container.setVisible(False)
            self.toggle_reset_btn.setText("Reset System")
        else:
            self.reset_container.setVisible(True)
            self.toggle_reset_btn.setText("Close")

    def reset(self) -> None:
        self.data_service.reset_data()

    def show_about(self) -> None:
        self.about = AboutDialog(self)
        self.about.move(0, 0)
        self.about.show()
        self.about.destroyed.connect(self.set_about_none)

    def set_about_none(self) -> None:
        self.about = None

    def resizeEvent(self, event):
        if self.about is not None:
            self.about.resize(self.size())
        super(ManageViewModel, self).resizeEvent(event)