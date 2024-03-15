import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from views.profile_view import ProfileView

# pyright: reportAttributeAccessIssue=false
# pyright: reportCallIssue=false

class TestProfileView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = ProfileView(self.viewmodel, self.parent, ui="src/views_ui/profile_view.ui")
        self.parent.show()

    def test_update_activities(self):
        self.view.update_activites([("title", "time", "description"), ("title", "time", "description"), ("title", "time", "description")])
        self.assertEqual(self.view.activity_container.count(), 3)

    def test_update_improvement_zero(self):
        self.view.update_improvements([])
        self.assertEqual(self.view.improvement_list.count(), 1)

    def test_update_improvement(self):
        self.view.update_improvements([("cat", -10), ("cat", -20)])
        self.assertEqual(self.view.improvement_list.count(), 2*2)

    def test_update_readings(self):
        self.view.update_readings([["title", True], ["title2", False]])
        self.assertEqual(self.view.reading_layout.count(), 2)

    def test_button_clicks(self):
        # Simulate button clicks
        QTest.mouseClick(self.view.award_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 0)

        QTest.mouseClick(self.view.improvement_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 1)
        
        QTest.mouseClick(self.view.reading_btn, Qt.LeftButton)
        self.assertEqual(self.view.stackedWidget.currentIndex(), 2)


