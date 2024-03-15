import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from views.learn_view import LearnView
from models.note import Note

# pyright: reportAttributeAccessIssue=false
# pyright: reportCallIssue=false

class TestLearnView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = LearnView(self.viewmodel, self.parent, ui="src/views_ui/learn_view.ui")
        self.parent.show()

    def test_load_titles(self):
        self.view.update_title_list([Note("note1", ""), Note("note2", "")])
        self.assertEqual(self.view.listWidget.count(), 2)

    def test_view_note(self):
        self.view.update_title_list([Note("note1", ""), Note("note2", "")])
        self.view.listWidget.setCurrentRow(1)
        self.view.note.view("<p>notes</p>")

        self.assertFalse(self.view.listWidget.item(0).isSelected())
        self.assertTrue(self.view.listWidget.item(1).isSelected())

        self.assertTrue(self.view.up_page_btn.isEnabled())
        self.assertFalse(self.view.down_page_btn.isEnabled())

        self.assertEqual(self.view.note.original_html, "<p>notes</p>")

    def test_menu_collapse(self):
        # Simulate button click
        QTest.mouseClick(self.view.expand_btn, Qt.LeftButton)
        self.assertFalse(self.view.menu.is_expanded)