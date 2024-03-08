import unittest
from models.user_preference import UserPreference

class TestUserPreference(unittest.TestCase):
    def setUp(self):
        self.preference = UserPreference()

    def test_to_json(self):
        expected_json = '{"start_up_index": 0, "custom_quiz_setting_expand": false, "show_notification": true}'
        self.assertEqual(self.preference.to_json(), expected_json)

    def test_from_json(self):
        json_string = '{"start_up_index": 2, "custom_quiz_setting_expand": true, "show_notification": false}'
        preference = UserPreference.from_json(json_string)
        self.assertEqual(preference.start_up_index, 2)
        self.assertTrue(preference.custom_quiz_setting_expand)
        self.assertFalse(preference.show_notification)