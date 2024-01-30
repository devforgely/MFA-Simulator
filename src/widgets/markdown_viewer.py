from PyQt5.QtWidgets import QTextEdit


class MarkdownViewer(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #d5d4d2;
                width: 15px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #bebdba;
                min-height: 20px;
            }
            QScrollBar:handle:vertical:hover {
                background: #777675;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def view(self, content):
        self.setHtml(content)
        