import unittest
from models.note import Note

class TestNote(unittest.TestCase):
    def setUp(self):
        self.note = Note("Test Note", "This is some *Markdown* content.")

    def test_no_content(self):
        note = Note(None, None)
        self.assertEqual(note.title, None)
        self.assertEqual(note.content, "")

    def test_content_property(self):
        # Initial content should be in Markdown format
        self.assertEqual(self.note.content, "<p>This is some <em>Markdown</em> content.</p>")

        # Modify content and check if it's converted to HTML
        self.note.content = "This is another **Markdown** content."
        self.assertEqual(self.note.content, "<p>This is another <strong>Markdown</strong> content.</p>")