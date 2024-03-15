import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from views.manage_view import ManageView

# pyright: reportAttributeAccessIssue=false
# pyright: reportCallIssue=false

class TestManageView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = ManageView(self.viewmodel, self.parent, ui="src/views_ui/manage_view.ui")
        self.parent.show()

    def test_start_up_combobox(self):
        self.view.update_start_up_combobox(0)
        self.assertTrue(self.view.default_location_btn.isChecked())
        self.assertFalse(self.view.start_up_combobox.isEnabled())
        self.view.update_start_up_combobox(1)
        self.assertFalse(self.view.default_location_btn.isChecked())
        self.assertTrue(self.view.custom_location_btn.isChecked())
        self.assertEqual(self.view.start_up_combobox.currentIndex(), 1)

    def test_default_location(self):
        # Simulate button click
        QTest.mouseClick(self.view.default_location_btn, Qt.LeftButton)
        self.assertTrue(self.view.default_location_btn.isChecked())
        self.assertFalse(self.view.start_up_combobox.isEnabled())

    def test_reset_dialog(self):
        # Simulate button click
        QTest.mouseClick(self.view.toggle_reset_btn, Qt.LeftButton)
        self.assertEqual(self.view.toggle_reset_btn.text(), "Close")
        self.assertTrue(self.view.reset_container.isVisible())
        QTest.mouseClick(self.view.toggle_reset_btn, Qt.LeftButton)
        self.assertEqual(self.view.toggle_reset_btn.text(), "Reset System")
        self.assertFalse(self.view.reset_container.isVisible())
        