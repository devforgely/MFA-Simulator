


class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content
    
    def get_content(self) -> str:
        return self.content