import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QPoint
from views.quiz_views import QuizSettingsView

# pyright: reportAttributeAccessIssue=false
# pyright: reportCallIssue=false

class TestQuizSettingsView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = QuizSettingsView(self.viewmodel, self.parent, ui="src/views_ui/quiz_settings_view.ui")
        self.parent.show()

    def test_setting_expand(self):
        self.assertTrue(self.view.config_box.isVisible())
        # Simulate button clicks
        QTest.mouseClick(self.view.collapsable_frame, Qt.LeftButton)
        self.assertFalse(self.view.config_box.isVisible())
        self.assertFalse(self.view.amend_btn.isVisible())

        QTest.mouseClick(self.view.collapsable_frame, Qt.LeftButton)
        self.assertTrue(self.view.config_box.isVisible())
        self.assertTrue(self.view.amend_btn.isVisible())

        QTest.mouseClick(self.view.classic_btn, Qt.LeftButton)
        self.viewmodel.set_classic.assert_called_once()

        QTest.mouseClick(self.view.timed_btn, Qt.LeftButton)
        self.viewmodel.set_timed.assert_called_once()

        QTest.mouseClick(self.view.improvement_btn, Qt.LeftButton)
        self.viewmodel.set_improvement.assert_called_once()

        QTest.mouseClick(self.view.amend_btn, Qt.LeftButton)
        self.viewmodel.validate_quiz_setting.assert_called_once()

    def test_category_box_visibility(self):
        QTest.mouseClick(self.view.all_categories_box, Qt.LeftButton)
        self.assertTrue(self.view.all_categories_box.isChecked())
        self.assertFalse(self.view.category_label.isVisible())
        self.assertFalse(self.view.category_combobox.isVisible())
        self.assertFalse(self.view.add_category_label.isVisible())
        self.assertFalse(self.view.category_scroll.isVisible())

        QTest.mouseClick(self.view.all_categories_box, Qt.LeftButton, pos=QPoint(2, int(self.view.all_categories_box.height()/2)))
        self.assertFalse(self.view.all_categories_box.isChecked())
        self.assertTrue(self.view.category_label.isVisible())
        self.assertTrue(self.view.category_combobox.isVisible())
        self.assertTrue(self.view.add_category_label.isVisible())
        self.assertTrue(self.view.category_scroll.isVisible())
    
    def test_timed_setting(self):
        QTest.mouseClick(self.view.timed_box, Qt.LeftButton)
        self.assertTrue(self.view.time_label.isVisible())
        self.assertTrue(self.view.time_field.isVisible())

        QTest.mouseClick(self.view.timed_box, Qt.LeftButton, pos=QPoint(2, int(self.view.all_categories_box.height()/2)))
        self.assertFalse(self.view.time_label.isVisible())
        self.assertFalse(self.view.time_field.isVisible())

    def test_add_category(self):
        self.viewmodel.is_text_in_list.return_value = False
        self.view.check_and_add_category()
        self.assertEqual(self.view.category_list.layout().count(), 1)

    def test_update_combobox(self):
        self.view.update_category_combobox(["item1", "item2"])
        self.assertEqual(self.view.category_combobox.count(), 2)

    