import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from views.help_view import HelpView

# pyright: reportAttributeAccessIssue=false
# pyright: reportCallIssue=false

class TestHelpView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.viewmodel = MagicMock()
        self.view = HelpView(self.viewmodel, ui="src/views_ui/help_view.ui")

    def test_button_click(self):
        # Simulate button click
        QTest.mouseClick(self.view.quick_start_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 0)

        # Simulate button click
        QTest.mouseClick(self.view.simulate_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 1)

        # Simulate button click
        QTest.mouseClick(self.view.learn_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 2)

        # Simulate button click
        QTest.mouseClick(self.view.quiz_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 3)

        # Simulate button click
        QTest.mouseClick(self.view.profile_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 4)

        # Simulate button click
        QTest.mouseClick(self.view.manage_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 5)


    def test_change_theme(self):
        # Simulate theme change button click
        QTest.mouseClick(self.view.theme_btn, Qt.LeftButton)
        self.assertEqual(self.view.current_theme, "dark")

        # toggle theme change button click
        QTest.mouseClick(self.view.theme_btn, Qt.LeftButton)
        self.assertEqual(self.view.current_theme, "light")

    def test_search(self):
        QTest.keyClicks(self.view.search_field, 'test text')
        QTest.keyClick(self.view.search_field, Qt.Key_Return)

        self.viewmodel.search.assert_called_once_with("test text")