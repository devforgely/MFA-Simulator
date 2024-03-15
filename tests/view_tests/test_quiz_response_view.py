import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from views.quiz_views import QuizResponseView

class TestQuizResponseView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.view = QuizResponseView(self.viewmodel, self.parent, ui="src/views_ui/quiz_response_view.ui")
        self.parent.show()

    def test_set_rank(self):
        self.view.set_rank(0.59)
        self.assertEqual(self.view.score_label.text(), "Test Failed")
        self.assertEqual(self.view.grade_text.text(), "Fail")

        self.view.set_rank(0.6)
        self.assertEqual(self.view.score_label.text(), "Test Passed")
        self.assertEqual(self.view.grade_text.text(), "Pass")


        self.view.set_rank(0.7)
        self.assertEqual(self.view.score_label.text(), "Test Passed")
        self.assertEqual(self.view.grade_text.text(), "Good")

        self.view.set_rank(0.8)
        self.assertEqual(self.view.score_label.text(), "Test Passed")
        self.assertEqual(self.view.grade_text.text(), "Great")

        self.view.set_rank(0.9)
        self.assertEqual(self.view.score_label.text(), "Test Passed")
        self.assertEqual(self.view.grade_text.text(), "Excellent")

    def test_update_time(self):
        self.view.update_time(True, 5, "01:20")
        self.assertTrue(self.view.time_val.text())

        self.view.update_time(False, 5, "01:20")
        self.assertEqual(self.view.time_val.text(), "01:20")

    def test_update_time_per_question(self):
        self.view.update_time_per_question("00:02")
        self.assertEqual(self.view.time_q_label.text(), "00:02")

    def test_update_difficulty(self):
        self.view.update_difficulty("1.2")
        self.assertEqual(self.view.difficulty_float.text(), "1.2")

    def test_update_score(self):
        self.view.update_score(4, 10)
        self.assertEqual(self.view.result_bar.value, 4)

    def test_update_detail_view(self):
        self.view.update_detail_view([{"question":"q1", "choices":["c1", "c2"], "answer":"c1"}], [("c1", True)], [("cat1", 33.3)])

        self.assertEqual(self.view.question_content.layout().count(), 2) # account for stretch

        self.assertEqual(self.view.percentage_display.layout().count(), 3) # account for stretch