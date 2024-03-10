from typing import Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from services.container import ApplicationContainer
from services.data_service import DataService
from viewmodels.main_viewmodel import MainViewModel
from viewmodels.help_viewmodel import HelpViewModel
from views.main_view import MainView
from views.help_view import HelpView
import sys
import ctypes


class App(QApplication):
    def __init__(self, sys_argv) -> None:
        super(App, self).__init__(sys_argv)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mfa.app')
        self.setWindowIcon(QIcon(u"icon.png"))

        self.message_service = ApplicationContainer.message_service()
        self.message_service.subscribe(self, DataService, self.on_message)
        self.message_service.subscribe(self, MainViewModel, self.on_message)

        self.main = MainView(MainViewModel())
        self.help = None
    
    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Help":
            self.help = HelpView(HelpViewModel())
        elif message_title == "Reboot":
            self.message_service.unsubscribe_all()

            previous_widgets = self.allWidgets()[:]

            self.main = MainView(MainViewModel())

            for widget in previous_widgets:
                widget.deleteLater()

            self.message_service.subscribe(self, DataService, self.on_message)
            self.message_service.subscribe(self, MainViewModel, self.on_message)


if __name__ == '__main__':
    app = App(sys.argv)
    app.aboutToQuit.connect(ApplicationContainer.data_service().save_data)
    sys.exit(app.exec_())