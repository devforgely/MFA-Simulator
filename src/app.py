import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from services.container import ApplicationContainer
from PyQt5.QtGui import QIcon
from viewmodels.main_viewmodel import MainViewModel


class App(QApplication):
    def __init__(self, sys_argv) -> None:
        super(App, self).__init__(sys_argv)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mfa.app')
        self.setWindowIcon(QIcon(u"icon.png"))
        self.main = MainViewModel()

if __name__ == '__main__':
    app = App(sys.argv)
    # app.aboutToQuit.connect(ApplicationContainer.data_service().save_data)
    sys.exit(app.exec_())