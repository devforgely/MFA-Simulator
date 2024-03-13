from PyQt5.QtCore import QObject, pyqtSignal
from services.container import ApplicationContainer
import string


class HelpViewModel(QObject):
    search_changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()

        self.data_service = ApplicationContainer.data_service()
        
        self.inverted_index, tokens = self.data_service.get_help_token()

        if tokens:
            for doc_id, text in tokens.items():
                if text:
                    self.add_document(doc_id, text)

    def add_document(self, doc_id, text):
        for term in text.split(' '):
            if term in self.inverted_index:
                self.inverted_index[term].add(doc_id)
            else:
                self.inverted_index[term] = {doc_id}

    def search(self, text: str) -> None:
        text = text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

        # Accumulate the indices for each term
        index_counts : dict[str, int] = {}
        for term in text.split(' '):
           indices = self.inverted_index.get(term, set())
           for index in indices:
               index_counts[index] = index_counts.get(index, 0) + 1

        # Get the most common index as the result
        self.search_changed.emit(int(max(index_counts, key=index_counts.get, default='0'))) # type: ignore

