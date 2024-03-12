import unittest
from unittest.mock import MagicMock, patch
from viewmodels.learn_viewmodel import LearnViewModel

class TestLearnViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.data_service')
    def setUp(self, data_service_mock):
        # Mocking data_service and its method get_notes
        self.mock_note = ["note1", "note2", "note3"]
        self.mock_content = "Note content"
        data_service_mock.return_value.get_notes.return_value = self.mock_note
        data_service_mock.return_value.read_note_content.return_value = self.mock_content
        self.view_model = LearnViewModel()

    def test_notes(self):
        # Mocking notes_changed signal
        self.view_model.notes_changed = MagicMock()

        # Calling the notes method
        self.view_model.notes()

        # Asserting if notes_changed.emit is called with the correct parameter
        self.view_model.notes_changed.emit.assert_called_once_with(self.mock_note)

    def test_note_content(self):
        # Mocking note_content_changed signal
        self.view_model.note_content_changed = MagicMock()

        # Calling the note_content method
        self.view_model.note_content(1)

        # Asserting if note_content_changed.emit is called with the correct parameter
        self.view_model.note_content_changed.emit.assert_called_once_with(self.mock_content)