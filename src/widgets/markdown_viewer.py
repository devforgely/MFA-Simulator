from PyQt5.QtWidgets import QTextBrowser

class MarkdownViewer(QTextBrowser):
    THEMES = {
        0: """
            QTextBrowser {
                padding-top: 10px;
                padding-left: 20px;
                font-family: arial;
                background-color: #f0f0f0;
                color: #000;
            }
        """,
        1: """
            QTextBrowser {
                padding-top: 10px;
                padding-left: 20px;
                font-family: arial;
                background-color: #fff5ee;
                color: #000;
            }
        """,
        2: """
            QTextBrowser {
                padding-top: 10px;
                padding-left: 20px;
                font-family: arial;
                background-color: #edd1b0;
                color: #000;
            }
        """,
        3: """
            QTextBrowser {
                padding-top: 10px;
                padding-left: 20px;
                font-family: arial;
                background-color: #f8fd98;
                color: #000;
            }
        """,
        4: """
            QTextBrowser {
                padding-top: 10px;
                padding-left: 20px;
                font-family: arial;
                background-color: #eddd63;
                color: #000;
            }
        """,
        5: """
            QTextBrowser {
                padding-top: 10px;
                padding-left: 20px;
                font-family: arial;
                background-color: #181a1b;
                color: #f5f4f3;
            }
        """
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_html = ""
        self.font_style = """
                            <style>
                                a { color: #5c94d9; }
                                p, li { font-size: 16px; }
                            </style>
                          """
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.set_scrollbar_style()

    def set_scrollbar_style(self):
        self.setStyleSheet("""
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

    def adjust_theme(self, theme: int) -> None:
        self.setStyleSheet(self.THEMES.get(theme, ""))

    def adjust_font_size(self, adjust: int) -> None:
        self.font_style = f"""
                            <style>
                                a {{ color: #5c94d9; }}
                                p, li {{ font-size: {16+adjust}px; }}
                            </style>
                           """
        if self.original_html:
            self.setHtml(self.font_style + self.original_html)

    def view(self, content) -> None:
        self.original_html = content
        self.setHtml(self.font_style + content)
