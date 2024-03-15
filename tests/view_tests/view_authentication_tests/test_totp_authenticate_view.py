import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from views.authentication.totp_view import TOTPAuthenticateView
from viewmodels.authentication.totp_viewmodel import TOTPAuthenticateViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestTotpAuthenticateView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
    
    @patch.object(TOTPAuthenticateViewModel, 'state_data')
    @patch.object(Settings, 'USER_FILE_PATH', new_callable=PropertyMock, return_value="tests/test_user.json")
    @patch.object(Settings, 'SIMULATION_NOTE_PATH', new_callable=PropertyMock, return_value="src/data/simulation_details/")
    @patch.object(Settings, 'NOTE_FILE_PATH', new_callable=PropertyMock, return_value="src/data/notes/")
    def setUp(self, note_file_path, simulation_note_path, user_file_path, mock_state_data):
        self.details = {}
        with open(f'src/data/simulation_details/totp.json', 'r') as file:
            self.details = json.load(file)["authentication"]
        self.parent = QWidget()
        
        ApplicationContainer.authentication_service().add(Method.TOTP)
        ApplicationContainer.authentication_service().register_count = 1

        mock_state_data.return_value = {"shared_key": ""}
        
        self.info_panel = InfoPanel(InfoMode.AUTHENTICATE, self.parent, ui_register="", ui_authenticate="src/views_ui/component_views/authenticate_info_view.ui")
        self.view = TOTPAuthenticateView(viewmodel=TOTPAuthenticateViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/authenticate_views/totp_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertNotEqual(self.info_panel.measure_bar.value(), 65)
        
    def test_update_state(self):
        self.view.update_state("test", 0)
        self.assertFalse(self.view.time_bar.isVisible())
        self.assertFalse(self.view.verify_btn.isEnabled())
        self.assertTrue(self.view.warning_label.isVisible())
        self.assertEqual(self.view.warning_label.text(), "test")

    def test_update_data(self):
        self.view.update_data({"timestamp_authenticate": "", "totp_entered": "", "sha1_hash": "", "totp": ""}, 1)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])

    def test_clear_input(self):
        for input in self.view.input_boxes:
            input.setText("12")

        self.view.clear_input()

        for input in self.view.input_boxes:
            self.assertEqual(input.text(), "")

    def test_update_code(self):
        self.view.update_code("111111", "12:00")

        self.assertEqual(self.view.code_label.text(), "111111")
        self.assertEqual(self.view.time_label.text(), "12:00")
        self.assertTrue(self.view.time_bar.isVisible())

    def test_update_time(self):
        self.view.update_time(10)
        self.assertEqual(self.view.time_bar.value(), 10)
        