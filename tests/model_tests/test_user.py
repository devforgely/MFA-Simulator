import unittest
from models.user import User, Badge

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User()

    def test_update_coins(self):
        initial_coins = self.user.coins
        self.user.update_coins(50)
        self.assertEqual(self.user.coins, initial_coins + 50)

    def test_increase_quiz_count(self):
        initial_quiz_count = self.user.quiz_completed
        self.user.increase_quiz_count()
        self.assertEqual(self.user.quiz_completed, initial_quiz_count + 1)

    def test_increase_simulation_count(self):
        initial_simulation_count = self.user.simulation_played
        self.user.increase_simulation_count()
        self.assertEqual(self.user.simulation_played, initial_simulation_count + 1)

    def test_add_badge(self):
        badge_to_add = Badge.LEARNER
        self.user.add_badge(badge_to_add)
        self.assertIn(badge_to_add.value, self.user.badges)

    def test_add_duplicate_badge(self):
        badge_to_add = Badge.LEARNER
        self.user.add_badge(badge_to_add)
        self.assertFalse(self.user.add_badge(badge_to_add))

    def test_update_improvements(self):
        initial_improvements_length = len(self.user.improvements)
        self.user.update_improvements([('category1', -10)])
        self.assertEqual(len(self.user.improvements), initial_improvements_length + 1)

    def test_update_improvements_positive_dont_exist(self):
        initial_improvements_length = len(self.user.improvements)
        self.user.update_improvements([('category1', 10)])
        self.assertEqual(len(self.user.improvements), initial_improvements_length)

    def test_update_improvements_positive_exist(self):
        self.user.improvements = [('category1', -20)]
        initial_improvements_length = len(self.user.improvements)
        self.user.update_improvements([('category1', 10)])
        self.assertEqual(len(self.user.improvements), initial_improvements_length)
        self.assertEqual(self.user.improvements[0][1], -10)
    
    def test_update_improvements_positive_remove(self):
        self.user.improvements = [('category1', -20)]
        initial_improvements_length = len(self.user.improvements)
        self.user.update_improvements([('category1', 20)])
        self.assertEqual(len(self.user.improvements), initial_improvements_length-1)

    def test_update_reading(self):
        self.user.readings = [(title, state) for title, state in zip(['title1', 'title2', 'title3'], [True, True, True])]
        title_to_update = 'title1'
        self.user.update_reading(title_to_update, False, 0)
        self.assertFalse(self.user.readings[0][1])

    def test_unlock_simulation(self):
        method_val = 0
        self.user.unlock_simulation(method_val)
        self.assertTrue(self.user.unlocked_simulations[method_val])

    def test_to_json(self):
        expected_json = '{"coins": 100, "quiz_completed": 0, "simulation_played": 0, "recent_activities": [], "badges": [], "improvements": [], "readings": [], "unlocked_simulations": {"1": true, "2": false, "3": false, "4": false, "5": false, "6": false, "7": false}}'
        self.assertEqual(self.user.to_json(), expected_json)

    def test_from_json(self):
        json_string = '{"coins": 100, "quiz_completed": 1, "simulation_played": 2, "recent_activities": [], "badges": [], "improvements": [], "readings": [], "unlocked_simulations": {"1": true, "2": false, "3": false, "4": false, "5": false, "6": false, "7": true}}'
        new_user = User.from_json(json_string)
        self.assertEqual(new_user.coins, 100)
        self.assertEqual(new_user.quiz_completed, 1)
        self.assertEqual(new_user.simulation_played, 2)
        self.assertFalse(new_user.recent_activities)
        self.assertFalse(new_user.badges)
        self.assertFalse(new_user.improvements)
        self.assertFalse(new_user.readings)
        self.assertTrue(new_user.unlocked_simulations[1])
        self.assertTrue(new_user.unlocked_simulations[7])
        self.assertFalse(new_user.unlocked_simulations[2])
