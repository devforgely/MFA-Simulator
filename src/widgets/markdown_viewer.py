from PyQt5.QtWidgets import QTextBrowser


class MarkdownViewer(QTextBrowser):
    def __init__(self, parent=None):
        QTextBrowser.__init__(self, parent)

        self.original_html = ""
        
        self.font_style = """<style>
                                a { color: #5c94d9; }
                                p { font-size: 16px; }
                                li { font-size: 16px; }
                            </style>"""

        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
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
        match theme:
            case 0:
                self.setStyleSheet("""
                                QTextBrowser {
                                    padding-top: 10px;
                                    padding-left: 20px;
                                    font-family: arial;
                                    background-color: #f0f0f0;
                                    color: #000;
                                }                                  
                                """)
            case 1:
                self.setStyleSheet("""
                                QTextBrowser {
                                    padding-top: 10px;
                                    padding-left: 20px;
                                    font-family: arial;
                                    background-color: #fff5ee;
                                    color: #000;
                                }                                  
                                """)
            case 2:
                self.setStyleSheet("""
                                QTextBrowser {
                                    padding-top: 10px;
                                    padding-left: 20px;
                                    font-family: arial;
                                    background-color: #edd1b0;
                                    color: #000;
                                }                                  
                                """)
            case 3:
                self.setStyleSheet("""
                                QTextBrowser {
                                    padding-top: 10px;
                                    padding-left: 20px;
                                    font-family: arial;
                                    background-color: #f8fd98;
                                    color: #000;
                                }                                  
                                """)
            case 4:
                self.setStyleSheet("""
                                QTextBrowser {
                                    padding-top: 10px;
                                    padding-left: 20px;
                                    font-family: arial;
                                    background-color: #eddd63;
                                    color: #000;
                                }                                  
                                """)
            case 5:
                self.setStyleSheet("""
                                QTextBrowser {
                                    padding-top: 10px;
                                    padding-left: 20px;
                                    font-family: arial;
                                    background-color: #181a1b;
                                    color: #f5f4f3;
                                }                                  
                                """)
    
    def adjust_font_size(self, adjust: int) -> None:
        self.font_style = f"""<style>
                    a {{ color: #5c94d9; }}
                    p {{ font-size: {16+adjust}px; }}
                    li {{ font-size: {16+adjust}px; }}
                </style>"""
        
        if self.original_html:
            self.setHtml(self.font_style + self.original_html)

    def view(self, content) -> None:
        self.original_html = content
        self.setHtml(self.font_style + content)
        