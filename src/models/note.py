import markdown


class Note:
    def __init__(self, title, content):
        self.title = title
        self._content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self,  content: str) -> None:
        self._content = markdown.markdown(content)