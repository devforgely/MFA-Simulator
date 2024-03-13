import unittest
from unittest.mock import patch, Mock
from viewmodels.help_viewmodel import HelpViewModel

class TestHelpViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.data_service")
    def setUp(self, mock_data_service):
        mock_data_service.return_value.get_help_token.return_value = ({}, {"1": ""})
        self.view_model = HelpViewModel()

    def test_add_document(self):
        self.view_model.add_document('0', 'text sample')
        self.view_model.add_document('1', 'text example')

        self.assertEqual(len(self.view_model.inverted_index), 3)
        self.assertTrue("text" in self.view_model.inverted_index)
        self.assertTrue("sample" in self.view_model.inverted_index)
        self.assertTrue("example" in self.view_model.inverted_index)

    def test_search(self):
        # Mocking inverted_index
        self.view_model.inverted_index = {'term1': {"1", "2", "3"}, 'term2': {"2", "3"}, 'term3': {"3"}}
        self.view_model.search_changed = Mock()

        # Setting up expected result
        expected_result = 3

        # Calling the search method
        self.view_model.search('Term1 term2 term3')

        # Asserting if search_changed.emit is called with the correct parameter
        self.view_model.search_changed.emit.assert_called_once_with(expected_result)