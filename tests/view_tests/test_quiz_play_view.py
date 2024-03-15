import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from views.quiz_views import QuizPlayView


class TestQuizPlayView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = QuizPlayView(self.viewmodel, self.parent, ui="src/views_ui/quiz_view.ui")
        self.parent.show()

    def test_set_timed(self):
        self.view.set_timed(True, 5, 20)
        self.assertTrue(self.view.time_bar.isVisible())
        self.assertTrue(self.view.time_label.isVisible())
        self.assertEqual(self.view.time_label.text(), "  5:00")

        self.view.set_timed(False, 5, 20)
        self.assertFalse(self.view.time_bar.isVisible())
        self.assertFalse(self.view.time_label.isVisible())

    def test_update_time_bar(self):
        self.view.update_time_bar(72, 1, 12)
        self.assertEqual(self.view.time_bar.value(), 72)
        self.assertEqual(self.view.time_label.text(), "  1:12")

    def test_update_quiz(self):
        self.view.update_quiz((1, {"question": "q1", "choices": ["c1", "c2"]}, "c2"), 3)
        
        self.assertEqual(self.view.question_label.text(), "1. q1")
        self.assertEqual(self.view.progress_label.text(), "<b>1</b> of <b>3</b> Questions")
        self.assertFalse(self.view.backward_btn.isEnabled())
        self.assertTrue(self.view.next_btn.isEnabled())