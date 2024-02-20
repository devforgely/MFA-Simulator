import sys
import ctypes
from typing import Any
from PyQt5.QtWidgets import QApplication
from services.container import ApplicationContainer
from data.data_service import DataService
from PyQt5.QtGui import QIcon
from viewmodels.main_viewmodel import MainViewModel


class App(QApplication):
    def __init__(self, sys_argv) -> None:
        super(App, self).__init__(sys_argv)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mfa.app')
        self.setWindowIcon(QIcon(u"icon.png"))

        self.message_service = ApplicationContainer.message_service()
        self.message_service.subscribe(self, DataService, self.on_message)
        self.main = MainViewModel()
    
    def on_message(self, message_title: str, *args: Any) -> None:
        if message_title == "Reboot":
            self.message_service.unsubscribe_all()
            old_main = self.main
            self.main = MainViewModel()
            old_main.close()


if __name__ == '__main__':
    app = App(sys.argv)
    app.aboutToQuit.connect(ApplicationContainer.data_service().save_data)
    sys.exit(app.exec_())