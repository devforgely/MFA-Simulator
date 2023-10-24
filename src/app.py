import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from viewmodels.main_viewmodel import MainViewModel


class App(QApplication):
    def __init__(self, sys_argv) -> None:
        super(App, self).__init__(sys_argv)

        self.stackpane = QStackedWidget()
        self.stackpane.setMinimumHeight(600)
        self.stackpane.setMinimumWidth(800)

        self.main = MainViewModel()
        
        self.stackpane.addWidget(self.main)
        self.stackpane.show()

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())