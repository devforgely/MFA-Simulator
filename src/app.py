import sys
from PyQt5 import QtWidgets
from viewmodels.MainViewModel import MainViewModel


class App(QtWidgets.QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        
        self.viewmodel = MainViewModel()
        self.viewmodel.show()

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())