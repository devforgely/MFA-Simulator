import unittest
from unittest.mock import MagicMock, patch
from viewmodels.simulate_viewmodels import SimulateViewModel, CreatorViewModel, RegisterViewModel, AuthenticateViewModel, Method

class TestSimulateViewModel(unittest.TestCase):
    @patch('services.container.ApplicationContainer.message_service')
    def setUp(self, message_service_mock):
        self.view_model = SimulateViewModel()

    def test_on_message_register_view(self):
        # Mocking change signal
        self.view_model.view_registration = MagicMock()

        # Call on_message with "Register View" message title
        self.view_model.on_message("Register View")

        # Assert that the view_registration signal is emitted
        self.view_model.view_registration.emit.assert_called_once()

    def test_on_message_authenticate_view(self):
        # Mocking change signal
        self.view_model.view_authentication = MagicMock()

        # Call on_message with "Authenticate View" message title
        self.view_model.on_message("Authenticate View")

        # Assert that the view_authentication signal is emitted
        self.view_model.view_authentication.emit.assert_called_once()

    def test_on_message_creator_view(self):
        # Mocking change signal
        self.view_model.view_creator = MagicMock()

        # Call on_message with "Creator View" message title
        self.view_model.on_message("Creator View")

        # Assert that the message_service send method is called with the correct parameters
        self.assertEqual(self.view_model.message_service.send.call_count, 2)

        # Assert that the view_creator signal is emitted
        self.view_model.view_creator.emit.assert_called_once()


class TestCreatorViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.data_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, message_service_mock, data_service_mock, authentication_service_mock):
        self.view_model = CreatorViewModel()

    def test_on_message_update_creator(self):
        # Mocking change signal
        self.view_model.simulation_changed = MagicMock()

        self.view_model.on_message("Update Creator")

        self.view_model.authentication_service.reset.assert_called_once()
        self.view_model.simulation_changed.emit.assert_called_once_with([], 0)

    def test_unlock_simulation_with_enough_coins(self):
        self.view_model.data_service.get_user_coins.return_value = 200
        
        self.assertTrue(self.view_model.unlock_simulation("Password"))
        self.view_model.data_service.update_user_coin.assert_called_once_with(-200)
        self.view_model.data_service.unlock_user_simulation.assert_called_once_with(1)
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Success Notification", "New simulation unlocked.")

    def test_unlock_simulation_with_insufficient_coins(self):
        self.view_model.data_service.get_user_coins.return_value = 199
        
        self.assertFalse(self.view_model.unlock_simulation("Password"))
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Warning Notification", "Please acquire at least 200 coins.")

    def test_update_simulation_add(self):
        # Mocking change signal
        self.view_model.simulation_changed = MagicMock()

        self.view_model.authentication_service.add.return_value = True
        self.view_model.authentication_service.get_all_types.return_value = [Method.PASSWORD]
        self.view_model.authentication_service.calculate_assurance_level.return_value = 1

        self.view_model.update_simulation("Password")

        self.view_model.authentication_service.add.assert_called_once_with(Method.PASSWORD)
        self.view_model.simulation_changed.emit.assert_called_once_with(["Password"], 1)

    def test_update_simulation_remove(self):
        # Mocking change signal
        self.view_model.simulation_changed = MagicMock()

        self.view_model.authentication_service.add.return_value = False
        self.view_model.authentication_service.get_all_types.return_value = []
        self.view_model.authentication_service.calculate_assurance_level.return_value = 0

        self.view_model.update_simulation("Password")

        self.view_model.authentication_service.remove.assert_called_once_with(Method.PASSWORD)
        self.view_model.simulation_changed.emit.assert_called_once_with([], 0)
   
    def test_simulate_with_can_simulate(self):
        self.view_model.authentication_service.can_simulate.return_value = True
        self.view_model.simulate()

        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Register View")

    def test_simulate_with_cannot_simulate(self):
        self.view_model.authentication_service.can_simulate.return_value = False
        self.view_model.simulate()

        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Error Notification", "Unable to simulate.")


class TestRegisterViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.data_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, message_service_mock, data_service_mock, authentication_service_mock):
        self.view_model = RegisterViewModel()

    @patch("services.container.ApplicationContainer.authentication_service")
    def test_on_message_register_view(self, authentication_service_mock):
        # Mocking change signals
        self.view_model.reset_signal = MagicMock()
        self.view_model.simulation_index_changed = MagicMock()

        self.view_model.authentication_service.get_type.return_value = Method.PASSWORD

        self.view_model.on_message("Register View")

        self.assertEqual(self.view_model.load_index, 1)
        self.view_model.reset_signal.emit.assert_called_once()
        self.view_model.simulation_index_changed.emit.assert_not_called()  # Because the simulation hasn't been loaded yet

    def test_on_message_registered(self):
        # Mocking change signals
        self.view_model.reset_signal = MagicMock()
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.at = 1
        self.view_model.authentication_service.register_count = 3

        self.view_model.on_message("Registered")

        self.view_model.reset_signal.emit.assert_not_called()
        self.view_model.simulation_index_changed.emit.assert_called_once_with(1, True, True)

    def test_load_simulation(self):
        # Mocking change signal
        self.view_model.simulation_load = MagicMock()

        # Set up test data
        self.view_model.message_service.subscribe.reset_mock()
        self.view_model.authentication_service.get_type.return_value = Method.PASSWORD
        viewmodel_mock = MagicMock()
        self.view_model.type_to_register[Method.PASSWORD] = MagicMock(return_value=viewmodel_mock)

        self.view_model.load_simulation()

        self.assertEqual(self.view_model.load_index, 1)
        self.view_model.message_service.subscribe.assert_called_once()
        self.view_model.simulation_load.emit.assert_called_once_with(viewmodel_mock)

    def test_go_forward(self):
        # Mocking change signal
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.go_authenticate.return_value = False
        self.view_model.authentication_service.forward.return_value = True
        self.view_model.load_index = 1
        self.view_model.authentication_service.at = 1
        self.view_model.authentication_service.register_count = 3

        self.view_model.go_forward()

        self.view_model.simulation_index_changed.emit.assert_called_once_with(1, True, True)

    def test_go_backward(self):
        # Mocking change signal
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.backward.return_value = True
        self.view_model.authentication_service.at = 2

        self.view_model.go_backward()

        self.view_model.simulation_index_changed.emit.assert_called_once_with(2, True, True)

    def test_end_simulation(self):
        self.view_model.end_simulation()

        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Creator View")


class TestAuthenticateViewModel(unittest.TestCase):
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, message_service_mock, authentication_service_mock):
        self.view_model = AuthenticateViewModel()

    @patch("services.container.ApplicationContainer.authentication_service")
    def test_on_message_authenticate_view(self, authentication_service_mock):
        # Mocking change signals
        self.view_model.reset_signal = MagicMock()
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.get_type.return_value = Method.FINGERPRINT

        self.view_model.on_message("Authenticate View")

        self.assertEqual(self.view_model.load_index, 1)
        self.view_model.reset_signal.emit.assert_called_once()
        self.view_model.simulation_index_changed.emit.assert_not_called()  # Because the simulation hasn't been loaded yet

    def test_on_message_authenticated(self):
        # Mocking change signals
        self.view_model.reset_signal = MagicMock()
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.at = 2
        self.view_model.authentication_service.auth_count = 3

        self.view_model.on_message("Authenticated")

        self.view_model.reset_signal.emit.assert_not_called()
        self.view_model.simulation_index_changed.emit.assert_called_once_with(2, True, True)

    def test_load_simulation(self):
        # Mocking change signal
        self.view_model.simulation_load = MagicMock()

        # Set up test data
        self.view_model.message_service.subscribe.reset_mock()
        self.view_model.authentication_service.get_type.return_value = Method.PASSWORD
        viewmodel_mock = MagicMock()
        self.view_model.type_to_authenticate[Method.PASSWORD] = MagicMock(return_value=viewmodel_mock)

        self.view_model.load_simulation()

        self.assertEqual(self.view_model.load_index, 1)
        self.view_model.message_service.subscribe.assert_called_once()
        self.view_model.simulation_load.emit.assert_called_once_with(viewmodel_mock)

    def test_go_forward(self):
        # Mocking change signal
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.go_finish.return_value = False
        self.view_model.authentication_service.forward.return_value = True
        self.view_model.load_index = 1
        self.view_model.authentication_service.at = 1
        self.view_model.authentication_service.auth_count = 3

        self.view_model.go_forward()

        self.view_model.simulation_index_changed.emit.assert_called_once_with(1, True, True)

    def test_go_forward_congrats(self):
        # Mocking change signal
        self.view_model.simulation_index_changed = MagicMock()
        self.view_model.congrats_dialog_signal = MagicMock()

        # Set up test data
        self.view_model.authentication_service.go_finish.return_value = True
        self.view_model.authentication_service.forward.return_value = False
        self.view_model.go_forward()

        self.view_model.simulation_index_changed.emit.assert_not_called()
        self.view_model.congrats_dialog_signal.emit.assert_called_once()


    def test_go_backward(self):
        # Mocking change signal
        self.view_model.simulation_index_changed = MagicMock()

        # Set up test data
        self.view_model.authentication_service.backward.return_value = True
        self.view_model.authentication_service.at = 2

        self.view_model.go_backward()

        self.view_model.simulation_index_changed.emit.assert_called_once_with(2, True, True)

    def test_end_simulation(self):
        self.view_model.end_simulation()

        self.view_model.authentication_service.complete_simulation.assert_not_called()
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Creator View")

    def test_complete_simulation(self):
        self.view_model.complete_simulation()

        self.view_model.authentication_service.complete_simulation.assert_called_once()
        self.view_model.message_service.send.assert_called_once_with(self.view_model, "Creator View")

    def test_bypass(self):
        # Mocking change signal
        self.view_model.bypass_signal = MagicMock()

        # Set up test data
        self.view_model.authentication_service.bypass.return_value = True
        self.view_model.authentication_service.at = 2

        self.view_model.bypass()

        self.view_model.bypass_signal.emit.assert_called_once_with(2)