import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from views.authentication.twofa_key_view import TwoFAKeyRegisterView
from viewmodels.authentication.twofa_key_viewmodel import TwoFAKeyRegisterViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestTwoFAKeyRegisterView(unittest.TestCase):
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
        with open(f'src/data/simulation_details/twofa_key.json', 'r') as file:
            self.details = json.load(file)["registration"]
        self.parent = QWidget()

        ApplicationContainer.authentication_service().add(Method.TWOFA_KEY)

        self.info_panel = InfoPanel(InfoMode.REGISTER, self.parent, ui_register="src/views_ui/component_views/register_info_view.ui", ui_authenticate="")
        self.view = TwoFAKeyRegisterView(viewmodel=TwoFAKeyRegisterViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/register_views/twofa_key_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertEqual(self.info_panel.measure_bar.value(), 95)
        
    def test_update_state(self):
        self.view.prepare_fingerprint(True)
        self.view.update_state("test", 0)
        self.assertTrue(self.view.instruction_label.isVisible())
        self.assertEqual(self.view.instruction_label.text(), "test")

    def test_update_data(self):
        self.view._viewmodel.key_name = "abc"
        self.view.update_data({"timestamp_register": "", "user_fingerprint": "", 
         "fingerprint_template": "", "private_key": "", "public_key": "", "key_handle": ""}, 0)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])

    def test_connect_device(self):
        self.view.connect_device()

        self.assertFalse(self.view.connect_btn.isVisible())
        self.assertFalse(self.view.waiting_label.isVisible())
        self.assertTrue(self.view.key_select_frame.isVisible())
        self.assertTrue(self.view.guide_label.isVisible())
        self.assertTrue(self.view.key_name_field.isVisible())
        self.assertTrue(self.view.next_btn.isVisible())

    def test_prepare_fingerprint(self):
        self.view.prepare_fingerprint(True)
        self.assertEqual(self.view.left_stacked.currentIndex(), 1)

