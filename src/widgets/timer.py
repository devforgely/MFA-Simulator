from PyQt5.QtCore import QThread, pyqtSignal
import time

class TimeThread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self, max_val):
        super(TimeThread, self).__init__()
        self.is_running = True
        self.step_duration = 0.5
        self.max_val = int(max_val / self.step_duration)
    
    def set_max(self, val: int) -> None:
        self.max_val = int(val / self.step_duration)

    def stop(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        for i in range(self.max_val-1, -1, -1):
            if not self.is_running:
                break
            self._signal.emit(i)
            time.sleep(self.step_duration)

class TimeDisplayThread(TimeThread):
    _signal = pyqtSignal(int, int, int)
    def __init__(self, max_val):
        super(TimeDisplayThread, self).__init__(max_val)
        self.mins = int(max_val // 60)
        self.sec = int(max_val % 60)

    def run(self):
        for i in range(self.max_val-1, -1, -1):
            if not self.is_running:
                break
            
            self._signal.emit(i, self.mins, self.sec)
            if i & 1 == 0:
                if self.sec == 0 and self.mins > 0:
                    self.sec = 59
                    self.mins -= 1
                else:
                    self.sec -= 1
            time.sleep(self.step_duration)