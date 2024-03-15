import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from views.authentication.chip_pin_view import ChipPinRegisterView
from viewmodels.authentication.chip_pin_viewmodel import ChipPinRegisterViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestChipPinRegisterView(unittest.TestCase):
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
        with open(f'src/data/simulation_details/chip_pin.json', 'r') as file:
            self.details = json.load(file)["registration"]
        self.parent = QWidget()

        ApplicationContainer.authentication_service().add(Method.CHIP_PIN)

        self.info_panel = InfoPanel(InfoMode.REGISTER, self.parent, ui_register="src/views_ui/component_views/register_info_view.ui", ui_authenticate="")
        self.view = ChipPinRegisterView(viewmodel=ChipPinRegisterViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/register_views/chip_pin_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertEqual(self.info_panel.measure_bar.value(), 90)
        
    def test_update_state(self):
        self.view.update_state("test", 0)
        self.assertFalse(self.view.submit_btn.isEnabled())
        self.assertFalse(self.view.clear_btn.isEnabled())
        self.assertTrue(self.view.warning_label.isVisible())

        self.view.update_state("test", 2)
        self.assertFalse(self.view.generate_pin_btn.isEnabled())

        self.view.update_state("test", 3)
        self.assertTrue(self.view.generate_pin_btn.isEnabled())

    def test_update_data(self):
        self.view.update_data({"timestamp_register": "", "user_pin": "", 
         "hashed_pin": "", "chip_details": "", "chip_digital_signature": ""}, 0)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])
