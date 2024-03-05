from PyQt5.QtWidgets import QLabel

class Heading1(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 30px;")

class Heading2(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")


class Picture(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setScaledContents(True)
        self.setStyleSheet("max-width: 700px; max-height: 445px; margin-bottom: 10px;")
