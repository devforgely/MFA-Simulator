import unittest
from unittest.mock import PropertyMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
from services.container import ApplicationContainer
from configuration.app_configuration import Settings
from views.authentication.totp_view import TOTPRegisterView
from viewmodels.authentication.totp_viewmodel import TOTPRegisterViewModel
from widgets.info_panel import *
from models.authentication.authentication import Method
import json


class TestTotpRegisterView(unittest.TestCase):
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
        with open(f'src/data/simulation_details/totp.json', 'r') as file:
            self.details = json.load(file)["registration"]
        self.parent = QWidget()

        ApplicationContainer.authentication_service().add(Method.TOTP)

        self.info_panel = InfoPanel(InfoMode.REGISTER, self.parent, ui_register="src/views_ui/component_views/register_info_view.ui", ui_authenticate="")
        self.view = TOTPRegisterView(viewmodel=TOTPRegisterViewModel(), info_panel=self.info_panel, parent=self.parent, ui="src/views_ui/register_views/totp_view.ui")
        self.parent.show()

    def test_info_panel(self):
        self.assertEqual(self.info_panel.about_description.text(), self.details["description"])
        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][0])
        self.assertEqual(self.info_panel.measure_bar.value(), 65)
        
    def test_update_state(self):
        self.view.update_state("test", 0)
        self.assertFalse(self.view.link_btn.isEnabled())
        self.assertFalse(self.view.cancel_btn.isEnabled())
        self.assertTrue(self.view.warning_label.isEnabled())
        self.assertEqual(self.view.warning_label.text(), "test")

    def test_update_data(self):
        self.view.update_data({"timestamp_register": "", "shared_key": ""}, 0)

        self.assertEqual(self.info_panel.data_note.text(), self.details["notes"][1])

    def test_cancel(self):
        self.view.cancel()

        self.assertEqual(self.view.left_stacked.currentIndex(), 0)
        self.assertEqual(self.view.phone_container.currentIndex(), 0)

    def test_update_phone_screen(self):
        self.view.update_phone_screen("abc", "23:31", "111.111", "asd12")

        self.assertEqual(self.view.phone_container.currentIndex(), 1)
        self.assertEqual(self.view.location_label.text(), "abc")
        self.assertEqual(self.view.time_label.text(), "23:31")
        self.assertEqual(self.view.device_label.text(), "111.111")
        self.assertEqual(self.view.user_label.text(), "asd12")
