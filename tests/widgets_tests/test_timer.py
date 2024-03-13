import unittest
from unittest.mock import MagicMock, patch
from widgets.timer import TimeThread, TimeDisplayThread

class TestTimeThread(unittest.TestCase):
    def setUp(self):
        self.thread = TimeThread(10)

    def test_init(self):
        self.assertTrue(self.thread.is_running)
        self.assertEqual(self.thread.max_val, 20)

    def test_set_max(self):
        self.thread.set_max(5)
        self.assertEqual(self.thread.max_val, 10)

    def test_stop(self):
        self.thread.stop()
        self.assertFalse(self.thread.is_running)

    @patch("time.sleep")
    def test_run(self, mock_sleep):
        self.thread._signal = MagicMock()

        self.thread.run()
        self.thread.wait()

        self.assertEqual(mock_sleep.call_count, 20)
        self.assertEqual(self.thread._signal.emit.call_count, 20)
        self.thread._signal.emit.called_with(0)

class TestTimeDisplayThread(unittest.TestCase):
    def setUp(self):
        self.thread = TimeDisplayThread(70)

    def test_init(self):
        self.assertEqual(self.thread.mins, 1)
        self.assertEqual(self.thread.sec, 10)

    @patch("time.sleep")
    def test_run(self, mock_sleep):
        self.thread._signal = MagicMock()

        self.thread.run()
        self.thread.wait()

        self.assertEqual(mock_sleep.call_count, 140)
        self.assertEqual(self.thread._signal.emit.call_count, 140)
        self.thread._signal.emit.called_with(0, 0, 0)
