import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from views.simulate_views import RegisterView


class TestRegisterView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = RegisterView(self.viewmodel, self.parent, ui="src/views_ui/register_view.ui")
        self.parent.show()

    def test_update_view(self):
        self.view.stackedWidget.addWidget(QWidget())
        self.view.update_view(0, True, False)

        self.assertFalse(self.view.next_btn.isEnabled())
        self.assertTrue(self.view.back_btn.isEnabled())
        self.assertEqual(self.view.stackedWidget.currentIndex(), 0)

        self.view.update_view(0, False, True)

        self.assertTrue(self.view.next_btn.isEnabled())
        self.assertFalse(self.view.back_btn.isEnabled())
        self.assertEqual(self.view.stackedWidget.currentIndex(), 0)

