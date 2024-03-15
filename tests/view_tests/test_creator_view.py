import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from views.simulate_views import CreatorView

class TestCreatorView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.parent = QWidget()
        self.viewmodel = MagicMock()
        self.viewmodel.unlocked_simulations = [("Password", True), ("Security Questions", True), ("Picture Password", True), 
                                                            ("Fingerprint Device", True), ("Chip && PIN", True), ("TOTP", True), ("2FA Key", True)]
        self.view = CreatorView(self.viewmodel, self.parent, ui="src/views_ui/creator_view.ui")
        self.parent.show()

    def test_update_simulation_details(self):
        self.view.update_simulation_details([], 0)

        self.assertEqual(self.view.measure_title.text(), "Select challenges from above to see Authenticator Assurance Level")

        self.view.update_simulation_details(["Password"], 1)

        self.assertEqual(self.view.measure_title.text(), "Authenticator Assurance Level 1")

        self.view.update_simulation_details(["Password", "Fingerprint Device"], 2)

        self.assertEqual(self.view.measure_title.text(), "Authenticator Assurance Level 2")

        self.view.update_simulation_details(["2FA Key"], 3)

        self.assertEqual(self.view.measure_title.text(), "Authenticator Assurance Level 3")