import unittest
from unittest.mock import MagicMock, patch
from viewmodels.authentication.picture_password_viewmodel import PicturePasswordRegisterViewModel, PicturePasswordAuthenticateViewModel, QWidget

class TestPicturePasswordRegisterViewModel(unittest.TestCase):
    @patch("os.listdir")
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service, mock_listdir):
        self.viewmodel = PicturePasswordRegisterViewModel()

    def test_refresh_images(self):
        spy = MagicMock()
        self.viewmodel.refresh_images_signal.connect(spy)

        self.viewmodel.images = [f"image{i}.png" for i in range(13)]

        # Case: Enough images available, should emit 9 images
        self.viewmodel.refresh_images()
        spy.assert_called_with(self.viewmodel.viewed_images[:9])

        # Case: Insufficient images available, should shuffle viewed_images
        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.viewed_images = ["image3.png", "image4.png", "image5.png"]
        self.viewmodel.refresh_images()
        self.assertEqual(len(self.viewmodel.viewed_images), 9)
        for image in self.viewmodel.selected_images:
            self.assertNotIn(image, self.viewmodel.viewed_images)

    @patch.object(PicturePasswordRegisterViewModel, "remove_selection")
    @patch.object(PicturePasswordRegisterViewModel, "add_selection")
    def test_on_image_click(self, mock_add, mock_remove):
        self.viewmodel.select_signal = MagicMock()

        self.viewmodel.selected_images = [f"image{i}.png" for i in range(3)]

        # Case: Add selection
        widget = MagicMock(spec=QWidget)
        widget.image = "image6.png"
        self.viewmodel.on_image_click(widget)
        self.viewmodel.select_signal.emit.assert_called_with(widget, True)
        mock_add.assert_called_once_with("image6.png")

        # Case: Remove selection
        widget.image = "image1.png"
        self.viewmodel.on_image_click(widget)
        self.viewmodel.select_signal.emit.assert_called_with(widget, False)
        mock_remove.assert_called_once_with("image1.png")

    def test_add_selection(self):
        # mock signals
        self.viewmodel.select_count_change = MagicMock()
        self.viewmodel.security_measure_changed = MagicMock()

        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.add_selection("image3.png")
        self.assertEqual(len(self.viewmodel.selected_images), 3)
        self.viewmodel.select_count_change.emit.assert_called_with("Selected Image Count: 3")
        self.viewmodel.security_measure_changed.emit.assert_called_with(30)

    def test_remove_selection(self):
        # mock signals
        self.viewmodel.select_count_change = MagicMock()
        self.viewmodel.security_measure_changed = MagicMock()

        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.remove_selection("image1.png")
        self.assertEqual(len(self.viewmodel.selected_images), 1)
        self.viewmodel.select_count_change.emit.assert_called_with("Selected Image Count: 1")
        self.viewmodel.security_measure_changed.emit.assert_called_with(10)

    def test_reset_selection(self):
        self.viewmodel.select_count_change = MagicMock()
        self.viewmodel.security_measure_changed = MagicMock()
        self.viewmodel.reset_selection_signal = MagicMock()

        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.reset_selection()
        self.assertEqual(len(self.viewmodel.selected_images), 0)
        self.viewmodel.select_count_change.emit.assert_called_once_with("Selected Image Count: 0")
        self.viewmodel.security_measure_changed.emit.assert_called_once_with(0)
        self.viewmodel.reset_selection_signal.emit.assert_called_once()

    def test_state_data(self):
        mock_data = {
            "user_images": [b"1.png", b"2.jpeg"],
            "hashed_secret": b"secret",
            "encryption_key": b"key",
            "iv": b"iv",
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data()
        self.assertTrue(isinstance(result["user_images"], str))
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertTrue(isinstance(result["encryption_key"], str))
        self.assertTrue(isinstance(result["iv"], str))

    @patch("viewmodels.authentication.picture_password_viewmodel.encrypt_images", return_value = b"encrypted_images")
    def test_send(self, mock_encrypt_images):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        # Case: No images selected
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Please select some images to proceed Registration.", 1)

        # Case: Registration successful
        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.authentication_service.register.return_value = True
        self.viewmodel.send()
        self.viewmodel.authentication_service.session_store.assert_called_once()
        self.viewmodel.state_change.emit.assert_called_with("Account has been registered.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(), 0)
        self.viewmodel.message_service.send.assert_called_with(self.viewmodel, "Registered")

        # Case: Registration failed
        self.viewmodel.authentication_service.register.return_value = False
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Registration Fail", 1)

class TestPicturePasswordAuthenticateViewModel(unittest.TestCase):
    @patch("os.listdir")
    @patch("services.container.ApplicationContainer.authentication_service")
    @patch("services.container.ApplicationContainer.message_service")
    def setUp(self, mock_message_service, mock_authentication_service, mock_listdir):
        self.viewmodel = PicturePasswordAuthenticateViewModel()

    def test_add_selection(self):
        # mock signals
        self.viewmodel.select_count_change = MagicMock()

        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.add_selection("image3.png")
        self.assertEqual(len(self.viewmodel.selected_images), 3)
        self.viewmodel.select_count_change.emit.assert_called_with("Selected Image Count: 3")

    def test_remove_selection(self):
        # mock signals
        self.viewmodel.select_count_change = MagicMock()

        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.remove_selection("image1.png")
        self.assertEqual(len(self.viewmodel.selected_images), 1)
        self.viewmodel.select_count_change.emit.assert_called_with("Selected Image Count: 1")

    def test_reset_selection(self):
        self.viewmodel.select_count_change = MagicMock()
        self.viewmodel.reset_selection_signal = MagicMock()

        self.viewmodel.selected_images = ["image1.png", "image2.png"]
        self.viewmodel.reset_selection()
        self.assertEqual(len(self.viewmodel.selected_images), 0)
        self.viewmodel.select_count_change.emit.assert_called_once_with("Selected Image Count: 0")
        self.viewmodel.reset_selection_signal.emit.assert_called_once()

    def test_state_data(self):
        mock_data = {
            "images": [b"1.png", b"2.jpeg"],
            "hashed_secret": b"secret",
            "nonce": b"nonce",
            "signed_challenge": b"signed_challenge",
            "expected_response": b"expected_response",
        }
        self.viewmodel.authentication_service.get_session_stored.return_value = mock_data

        result = self.viewmodel.state_data(False)
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertFalse(isinstance(result["images"], str))
        self.assertFalse(isinstance(result["signed_challenge"], str))
        self.assertFalse(isinstance(result["expected_response"], str))

        result = self.viewmodel.state_data(True)
        self.assertTrue(isinstance(result["hashed_secret"], str))
        self.assertTrue(isinstance(result["images"], str))
        self.assertTrue(isinstance(result["nonce"], str))
        self.assertTrue(isinstance(result["signed_challenge"], str))
        self.assertTrue(isinstance(result["expected_response"], str))

    @patch("viewmodels.authentication.picture_password_viewmodel.encrypt_images", return_value = b"encrypted_images")
    def test_send(self, mock_encrypt_images):
        # mock signals
        self.viewmodel.state_change = MagicMock()
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.authentication_service.get_session_stored.return_value = {"encryption_key": b"key", "iv": b"iv"}

        # Case: Successful authentication
        self.viewmodel.authentication_service.authenticate.return_value = 0
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("The user has been authenticated.", 0)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(True), 0)
        self.viewmodel.message_service.send.assert_called_once_with(self.viewmodel, "Authenticated")

        # Case: Incorrect
        self.viewmodel.authentication_service.authenticate.return_value = 1
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("These credentials does not match our records.", 1)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 1)

        # Case: Locked for 10 seconds
        self.viewmodel.authentication_service.authenticate.return_value = 2
        self.viewmodel.send()
        self.viewmodel.state_change.emit.assert_called_with("Locked for 10 seconds.", 2)
        self.viewmodel.state_data_change.emit.assert_called_with(self.viewmodel.state_data(False), 2)


    def test_bypass(self):
        # mock signals
        self.viewmodel.state_data_change = MagicMock()
        self.viewmodel.state_data = MagicMock()
        self.viewmodel.state_data.return_value = {}

        self.viewmodel.bypass()
        self.viewmodel.state_data_change.emit.assert_called_once_with(self.viewmodel.state_data(True), 0)
    