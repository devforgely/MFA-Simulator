import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from views.authentication.picture_password_view import PicturePasswordAuthenticateView
from viewmodels.authentication.picture_password_viewmodel import PicturePasswordAuthenticateViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestPicturePasswordAuthenticateView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
    
    @patch.object(PicturePasswordAuthenticateViewModel, 'state_data')
    @patch.object(Settings, 'PICTURE_FILE_PATH', new_callable=PropertyMock, return_value="src/data/images/")
    @patch.object(Settings, 'USER_FILE_PATH', new_callable=PropertyMock, return_value="tests/test_user.json")
    @patch.object(Settings, 'SIMULATION_NOTE_PATH', new_callable=PropertyMock, return_value="src/data/simulation_details/")
    @patch.object(Settings, 'NOTE_FILE_PATH', new_callable=PropertyMock, return_value="src/data/notes/")
    def setUp(self, note_file_path, simulation_note_path, user_file_path, picture_path, mock_state_data):
        self.details = {}
        with open(f'src/data/simulation_details/picture_password.json', 'r') as file:
            self.details = json.load(file)["authentication"]
        self.parent = QWidget()
        
        ApplicationContainer.authentication_service().add(Method.PICTURE_PASSWORD)
        ApplicationContainer.authentication_service().register_count = 1

        mock_state_data.return_value = {"hashed_secret": ""}
        
        self.info_panel = InfoPanel(InfoMode.AUTHENTICATE, self.parent, ui_register="", ui_authenticate="src/views_ui/component_views/authenticate_info_view.ui")
        self.view = PicturePasswordAuthenticateView(viewmodel=PicturePasswordAuthenticateViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/authenticate_views/picture_password_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertNotEqual(self.info_panel.measure_bar.value(), 0)

    def test_update_data(self):
        self.view.update_data({"timestamp_authenticate": "", "images": "", "nonce": "", "signed_challenge": "", "expected_response": ""}, 1)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])