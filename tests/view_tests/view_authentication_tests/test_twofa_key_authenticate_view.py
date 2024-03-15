import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from services.authentication_service import AuthenticationService
from configuration.app_configuration import Settings
from views.authentication.twofa_key_view import TwoFAKeyAuthenticateView
from viewmodels.authentication.twofa_key_viewmodel import TwoFAKeyAuthenticateViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestwoFAKeyAuthenticateView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
    
    @patch.object(TwoFAKeyAuthenticateViewModel, 'state_data')
    @patch.object(Settings, 'USER_FILE_PATH', new_callable=PropertyMock, return_value="tests/test_user.json")
    @patch.object(Settings, 'SIMULATION_NOTE_PATH', new_callable=PropertyMock, return_value="src/data/simulation_details/")
    @patch.object(Settings, 'NOTE_FILE_PATH', new_callable=PropertyMock, return_value="src/data/notes/")
    def setUp(self, note_file_path, simulation_note_path, user_file_path, mock_state_data):
        self.details = {}
        with open(f'src/data/simulation_details/twofa_key.json', 'r') as file:
            self.details = json.load(file)["authentication"]
        self.parent = QWidget()
        
        ApplicationContainer.authentication_service().add(Method.TWOFA_KEY)
        ApplicationContainer.authentication_service().register_count = 1
        ApplicationContainer.authentication_service().session_store({"key_name":"abc"})

        mock_state_data.return_value = {"fingerprint_template": "", "private_key": "", "public_key": "", "key_handle": ""}
        
        self.info_panel = InfoPanel(InfoMode.AUTHENTICATE, self.parent, ui_register="", ui_authenticate="src/views_ui/component_views/authenticate_info_view.ui")
        self.view = TwoFAKeyAuthenticateView(viewmodel=TwoFAKeyAuthenticateViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/authenticate_views/twofa_key_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertNotEqual(self.info_panel.measure_bar.value(), 95)
        
    def test_update_state(self):
        self.view.update_state("test", 0)
        self.assertTrue(self.view.warning_label.isVisible())
        self.assertEqual(self.view.warning_label.text(), "test")

    def test_update_data(self):
        self.view.update_data({"timestamp_authenticate": "", "fingerprint": "", "similarity_score": ""}, 1)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])

    def test_connect_device(self):
        self.view.connect_device()

        self.assertFalse(self.view.connect_btn.isVisible())
        self.assertFalse(self.view.waiting_label.isVisible())
        self.assertTrue(self.view.key_select_frame.isVisible())
        self.assertTrue(self.view.fingerprint.isVisible())
        self.assertTrue(self.view.instruction_label.isVisible())