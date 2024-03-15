import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from views.authentication.password_view import PasswordRegisterView
from viewmodels.authentication.password_viewmodel import PasswordRegisterViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestPasswordRegisterView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    @patch.object(Settings, 'USER_FILE_PATH', new_callable=PropertyMock, return_value="tests/test_user.json")
    @patch.object(Settings, 'SIMULATION_NOTE_PATH', new_callable=PropertyMock, return_value="src/data/simulation_details/")
    @patch.object(Settings, 'NOTE_FILE_PATH', new_callable=PropertyMock, return_value="src/data/notes/")
    def setUp(self, note_file_path, simulation_note_path, user_file_path):
        self.details = {}
        with open(f'src/data/simulation_details/password.json', 'r') as file:
            self.details = json.load(file)["registration"]
        self.parent = QWidget()

        ApplicationContainer.authentication_service().add(Method.PASSWORD)

        self.info_panel = InfoPanel(InfoMode.REGISTER, self.parent, ui_register="src/views_ui/component_views/register_info_view.ui", ui_authenticate="")
        self.view = PasswordRegisterView(viewmodel=PasswordRegisterViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/register_views/password_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertEqual(self.info_panel.measure_bar.value(), 0)
        
    def test_update_state(self):
        self.view.update_state("test", 0)
        self.assertFalse(self.view.submit_btn.isEnabled())
        self.assertTrue(self.view.warning_label.isVisible())

    def test_update_data(self):
        self.view.update_data({"timestamp_register": "", "user_registered": "", 
         "user_password": "", "hashed_secret": "", "salt": ""}, 0)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])
