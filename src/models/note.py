import markdown


class Note:
    def __init__(self, title, content):
        self.title = title
        if content:
            self._content = markdown.markdown(content)
        else:
            self._content = ""

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self,  content: str) -> None:
        self._content = markdown.markdown(content)