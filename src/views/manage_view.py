from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from widgets.dialog import AboutDialog
from configuration.app_configuration import Settings


class ManageView(QWidget):
    def __init__(self, viewmodel, parent: QWidget) -> None:
        super().__init__(parent)
        uic.loadUi("views_ui/manage_view.ui", self)
        
        self._viewmodel = viewmodel
        self._viewmodel.start_up_changed.connect(self.update_start_up_combobox)
        self._viewmodel.quiz_expand_changed.connect(self.expand_toggle.setChecked)
        self._viewmodel.notification_toggle_changed.connect(self.notification_toggle.setChecked)
        
        self.setup_ui()

        self._viewmodel.start_up_index()
        self._viewmodel.quiz_expand_toggle()
        self._viewmodel.notification_toggle()

    def setup_ui(self) -> None:
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

        self.default_location_btn.clicked.connect(self.set_default_location)
        self.custom_location_btn.clicked.connect(lambda: self.start_up_combobox.setEnabled(True))
        self.start_up_combobox.currentIndexChanged.connect(lambda i: self._viewmodel.change_start_up_index(i))

        self.expand_toggle.clicked.connect(lambda state: self._viewmodel.change_quiz_expand(state))

        self.notification_toggle.clicked.connect(lambda state: self._viewmodel.change_notification_state(state))

        self.about_label.clicked.connect(self.show_about)

        self.toggle_reset_btn.clicked.connect(self.toggle_reset)
        self.reset_btn.clicked.connect(self._viewmodel.reset_application)

    def update_start_up_combobox(self, index: int) -> None:
        if index == 0:
            self.default_location_btn.setChecked(True)
            self.start_up_combobox.setEnabled(False)
        else:
            self.custom_location_btn.setChecked(True)
            self.start_up_combobox.setCurrentIndex(index)

    def set_default_location(self) -> None:
        self._viewmodel.change_start_up_index(0)
        self.start_up_combobox.setEnabled(False)

    def toggle_reset(self) -> None:
        if self.reset_container.isVisible():
            self.reset_container.setVisible(False)
            self.toggle_reset_btn.setText("Reset System")
        else:
            self.reset_container.setVisible(True)
            self.toggle_reset_btn.setText("Close")

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
        super(ManageView, self).resizeEvent(event)