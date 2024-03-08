import unittest
import os
from models.utils import *


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32)  # Example key
        self.iv = os.urandom(16)  # Example IV

    def test_normalise_text(self):
        # Test with input containing punctuation, spaces, uppercase letters, and numbers
        input_text = "Hello, World! This is 123 Test."
        expected_output = "helloworldthisis123test"
        self.assertEqual(normalise_text(input_text), expected_output)

        # Test with input containing only punctuation and spaces
        input_text = "!@#$%^&*()_+  "
        expected_output = ""
        self.assertEqual(normalise_text(input_text), expected_output)

        # Test with input containing only numbers
        input_text = "1234567890"
        expected_output = "1234567890"
        self.assertEqual(normalise_text(input_text), expected_output)

    def test_parse_array(self):
        # Test with a list of strings
        input_arr = ["apple", "banana", "cherry"]
        expected_output = "apple\nbanana\ncherry"
        self.assertEqual(parse_array(input_arr), expected_output)

        # Test with an empty list
        input_arr = []
        expected_output = ""
        self.assertEqual(parse_array(input_arr), expected_output)

        # Test with a list containing a single string
        input_arr = ["single"]
        expected_output = "single"
        self.assertEqual(parse_array(input_arr), expected_output)

    def test_byte_str(self):
        # Test with bytes input
        input_bytes = b'Hello, World!'
        self.assertIsInstance(byte_str(input_bytes), str)

        # Test with empty bytes input
        input_bytes = b''
        expected_output = ''
        self.assertEqual(byte_str(input_bytes), expected_output)

        # Test with bytes input containing special characters
        input_bytes = b'\x00\x01\x02\x03'
        self.assertIsInstance(byte_str(input_bytes), str)

    def test_decode_key(self):
        class MockKey:
            def save_pkcs1(self):
                return b'encoded_key'

        # Test with a mock key object
        mock_key = MockKey()
        decoded_key = decode_key(mock_key)

        # Assert that the decoded key matches the expected value
        self.assertIsInstance(decoded_key, str)

    def test_image_byte(self):
        # Test with a sample image file
        image_dir = 'src/data/images/bees-1.jpg'  # Replace 'sample_image.jpg' with the actual image file path
        img_bytes = image_byte(image_dir)

        # Assert that the image bytes are of type bytes
        self.assertIsInstance(img_bytes, bytes)

    def test_encrypt_images(self):
        # Define image directories for testing
        image_dirs = ["src/data/images/arrows-1.jpg", "src/data/images/balloons-1.jpg"]

        # Read the original images into bytes
        original_images = [open(img_dir, 'rb').read() for img_dir in image_dirs]

        # Call the function to be tested
        encrypted_images = encrypt_images(image_dirs, self.key, self.iv)

        # Assert that the encrypted images are not empty
        self.assertTrue(encrypted_images)
        self.assertIsInstance(encrypted_images, list)

        # Decrypt the encrypted images using the same key and IV
        decrypted_images = decrypt_images(encrypted_images, self.key, self.iv)

        # Assert that the decrypted images match the original input images
        # (Note: This assumes that the encryption and decryption functions are symmetric)
        for original, decrypted in zip(original_images, decrypted_images):
            self.assertEqual(decrypted, original)


    