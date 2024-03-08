import unittest
from models.authentication.authentication_methods import *


class TestChipPinStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = ChipPinStrategy()

    def test_get_type(self):
        # Assert
        self.assertEqual(self.strategy.get_type(), Method.CHIP_PIN)

    def test_register(self):
        # Arrange
        pin = "1234"

        # Act
        result = self.strategy.register(pin)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_register" in self.strategy.data)
        self.assertTrue("user_pin" in self.strategy.data)
        self.assertEqual(self.strategy.data["user_pin"], pin)
        self.assertTrue("hashed_pin" in self.strategy.data)
        self.assertTrue("chip_details" in self.strategy.data)
        self.assertTrue("chip_digital_signature" in self.strategy.data)

    def test_register_false(self):
        # Arrange
        pin = ""

        # Act
        result = self.strategy.register(pin)

        # Assert
        self.assertFalse(result)
        self.assertFalse("timestamp_register" in self.strategy.data)
        self.assertFalse("user_pin" in self.strategy.data)
        self.assertFalse("hashed_pin" in self.strategy.data)
        self.assertFalse("chip_details" in self.strategy.data)
        self.assertFalse("chip_digital_signature" in self.strategy.data)

    def test_authenticate(self):
        # Arrange
        pin = "1234"
        self.strategy.register(pin)

        # Act
        result = self.strategy.authenticate(pin)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["pin"], pin)
        self.assertTrue("arqc" in self.strategy.data)
        self.assertTrue("arpc" in self.strategy.data)

    def test_authenticate_false(self):
        # Arrange
        pin = "1234"
        self.strategy.register(pin)

        # Act
        result = self.strategy.authenticate("0234")

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertTrue("pin", pin)
        self.assertFalse("arqc" in self.strategy.data)
        self.assertFalse("arpc" in self.strategy.data)

    def test_bypass(self):
        # Arrange
        pin = "1234"
        self.strategy.register(pin)

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertTrue("pin", self.strategy.data["user_pin"])
        self.assertTrue("arqc" in self.strategy.data)
        self.assertTrue("arpc" in self.strategy.data)


class TestFingerPrintStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = FingerPrintStrategy()

    def test_get_type(self):
        # Assert
        self.assertEqual(self.strategy.get_type(), Method.FINGERPRINT)

    def test_register(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        
        # Act
        result = self.strategy.register(fingerprint)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_register" in self.strategy.data)
        self.assertEqual(self.strategy.data["user_fingerprint"], fingerprint)
        self.assertTrue("fingerprint_template" in self.strategy.data)

    def test_register_false(self):
        # Arrange
        fingerprint = b''
        
        # Act
        result = self.strategy.register(fingerprint)

        # Assert
        self.assertFalse(result)
        self.assertFalse("timestamp_register" in self.strategy.data)
        self.assertFalse("user_fingerprint" in self.strategy.data)
        self.assertFalse("fingerprint_template" in self.strategy.data)

    def test_authenticate(self):
        self.strategy = FingerPrintStrategy()
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        self.strategy.register(fingerprint)

        # Act
        result = self.strategy.authenticate(fingerprint)

        # Assert
        self.assertEqual(self.strategy.data["user_fingerprint"], fingerprint)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["fingerprint"], fingerprint)

    def test_authenticate_false(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        self.strategy.register(fingerprint)

        # Act
        result = self.strategy.authenticate(b'\x01\x02\x03\x04\x06')

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["fingerprint"], b'\x01\x02\x03\x04\x06')

    def test_bypass(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        self.strategy.register(fingerprint)

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertTrue("fingerprint", self.strategy.data["user_fingerprint"])


class TestPicturePasswordStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = PicturePasswordStrategy()

    def test_get_type(self):
        # Assert
        self.assertEqual(self.strategy.get_type(), Method.PICTURE_PASSWORD)

    def test_register(self):
        # Arrange
        images = [b'image1', b'image2', b'image3']

        # Act
        result = self.strategy.register(images)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_register" in self.strategy.data)
        self.assertEqual(self.strategy.data["user_images"], images)
        self.assertTrue("hashed_secret" in self.strategy.data)

    def test_register_false(self):
        # Arrange
        images = []

        # Act
        result = self.strategy.register(images)

        # Assert
        self.assertFalse(result)
        self.assertFalse("timestamp_register" in self.strategy.data)
        self.assertFalse("user_images" in self.strategy.data)
        self.assertFalse("hashed_secret" in self.strategy.data)

    def test_challenge_response(self):
        # Arrange
        images = [b'image1', b'image2', b'image3']
        self.strategy.register(images)

        # Act
        self.strategy.challenge_response(images)

        # Assert
        self.assertTrue("nonce" in self.strategy.data)
        self.assertTrue("signed_challenge" in self.strategy.data)
        self.assertTrue("expected_response" in self.strategy.data)

    def test_authenticate(self):
        # Arrange
        images = [b'image1', b'image2', b'image3']
        self.strategy.register(images)

        # Act
        result = self.strategy.authenticate(images)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["images"], images)
        self.assertTrue("nonce" in self.strategy.data)
        self.assertTrue("signed_challenge" in self.strategy.data)
        self.assertTrue("expected_response" in self.strategy.data)

    def test_authenticate_false(self):
        # Arrange
        images = [b'image1', b'image2', b'image3']
        self.strategy.register(images)

        # Act
        result = self.strategy.authenticate([b'image1', b'image2', b'image4'])

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["images"], [b'image1', b'image2', b'image4'])
        self.assertTrue("nonce" in self.strategy.data)
        self.assertTrue("signed_challenge" in self.strategy.data)
        self.assertTrue("expected_response" in self.strategy.data)

    def test_bypass(self):
        # Arrange
        images = [b'image1', b'image2', b'image3']
        self.strategy.register(images)

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["images"], self.strategy.data["user_images"])


class TestPasswordStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = PasswordStrategy()

    def test_get_type(self):
        # Assert
        self.assertEqual(self.strategy.get_type(), Method.PASSWORD)

    def test_register(self):
        # Arrange
        username = "test_user"
        password = "test_password"

        # Act
        result = self.strategy.register(username, password)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_register" in self.strategy.data)
        self.assertEqual(self.strategy.data["user_registered"], username)
        self.assertEqual(self.strategy.data["user_password"], password)
        self.assertTrue("salt" in self.strategy.data)
        self.assertTrue("hashed_secret" in self.strategy.data)

    def test_register_empty_username(self):
        # Arrange
        username = ""
        password = "test_password"

        # Act
        result = self.strategy.register(username, password)

        # Assert
        self.assertFalse(result)
        self.assertFalse("user_registered" in self.strategy.data)
        self.assertFalse("user_password" in self.strategy.data)
        self.assertFalse("salt" in self.strategy.data)
        self.assertFalse("hashed_secret" in self.strategy.data)

    def test_register_empty_password(self):
        # Arrange
        username = "user"
        password = ""

        # Act
        result = self.strategy.register(username, password)

        # Assert
        self.assertFalse(result)
        self.assertFalse("user_registered" in self.strategy.data)
        self.assertFalse("user_password" in self.strategy.data)
        self.assertFalse("salt" in self.strategy.data)
        self.assertFalse("hashed_secret" in self.strategy.data)

    def test_register_empty_inputs(self):
        # Arrange
        username = ""
        password = ""

        # Act
        result = self.strategy.register(username, password)

        # Assert
        self.assertFalse(result)
        self.assertFalse("user_registered" in self.strategy.data)
        self.assertFalse("user_password" in self.strategy.data)
        self.assertFalse("salt" in self.strategy.data)
        self.assertFalse("hashed_secret" in self.strategy.data)

    def test_authenticate(self):
        # Arrange
        username = "test_user"
        password = "test_password"
        self.strategy.register(username, password)

        # Act
        result = self.strategy.authenticate(username, password)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["username"], username)
        self.assertEqual(self.strategy.data["password"], password)

    
    def test_authenticate_false_user(self):
        # Arrange
        username = "test_user"
        password = "test_password"
        self.strategy.register(username, password)

        # Act
        result = self.strategy.authenticate("wrong", password)

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["username"], "wrong")
        self.assertEqual(self.strategy.data["password"], password)

    def test_authenticate_false_password(self):
        # Arrange
        username = "test_user"
        password = "test_password"
        self.strategy.register(username, password)

        # Act
        result = self.strategy.authenticate(username, "wrong")

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["username"], username)
        self.assertEqual(self.strategy.data["password"], "wrong")

    def test_authenticate_false_inputs(self):
        # Arrange
        username = "test_user"
        password = "test_password"
        self.strategy.register(username, password)

        # Act
        result = self.strategy.authenticate("wrong_user", "wrong_password")

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["username"], "wrong_user")
        self.assertEqual(self.strategy.data["password"], "wrong_password")

    def test_bypass(self):
        # Arrange
        username = "test_user"
        password = "test_password"
        self.strategy.register(username, password)

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["username"], self.strategy.data["user_registered"])
        self.assertEqual(self.strategy.data["password"], self.strategy.data["user_password"])


class TestTOTPStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = TOTPStrategy()

    def test_get_type(self):
        # Assert
        self.assertEqual(self.strategy.get_type(), Method.TOTP)

    def test_register_false(self):
        # Arrange
        request = ""

        # Act
        result = self.strategy.register(request)

        # Assert
        self.assertFalse(result)
        self.assertTrue("shared_key" in self.strategy.data)
    
    def test_register(self):
        # Arrange
        request = "Confirm key"

        # Act
        result_1 = self.strategy.register("")
        result_2 = self.strategy.register(request)

        # Assert
        self.assertFalse(result_1)
        self.assertTrue(result_2)
        self.assertTrue("shared_key" in self.strategy.data)
        self.assertTrue("timestamp_register" in self.strategy.data)

    def test_totp(self):
        # Arrange
        self.strategy.register("")
        self.strategy.register("Confirm")

        totp = self.strategy.generate_TOTP()

        self.assertEqual(len(totp), 6)
        self.assertTrue(totp.isdigit())

    def test_authenticate(self):
        # Arrange
        self.strategy.register("")
        self.strategy.register("Confirm")

        # Act
        result_1 = self.strategy.authenticate("GENERATE")
        result_2 = self.strategy.authenticate(self.strategy.data["totp"])

        # Assert
        self.assertFalse(result_1)
        self.assertTrue(result_2)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertTrue("totp" in self.strategy.data)
        self.assertEqual(self.strategy.data["totp_entered"], self.strategy.data["totp"])

    def test_authenticate_false(self):
        # Arrange
        self.strategy.register("")
        self.strategy.register("Confirm")

        # Act
        result_1 = self.strategy.authenticate("GENERATE")
        result_2 = self.strategy.authenticate("000000")

        # Assert
        self.assertFalse(result_1)
        self.assertFalse(result_2)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertTrue("totp" in self.strategy.data)
        self.assertEqual(self.strategy.data["totp_entered"], "000000")
        self.assertTrue("sha1_hash" in self.strategy.data)

    def test_bypass(self):
        # Arrange
        self.strategy.register("")
        self.strategy.register("Confirm")

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertTrue("totp" in self.strategy.data)
        self.assertEqual(self.strategy.data["totp_entered"], self.strategy.data["totp"])
        self.assertTrue("sha1_hash" in self.strategy.data)


class TestSecurityQuestionStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = SecurityQuestionStrategy()

    def test_get_type(self):
        # Assert
        self.assertEqual(self.strategy.get_type(), Method.SECRET_QUESTION)

    def test_register(self):
        # Arrange
        questions = ["What is your favorite color?", "What is your pet's name?"]
        answers = "blue$dog"

        # Act
        result = self.strategy.register(questions, answers)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_register" in self.strategy.data)
        self.assertEqual(self.strategy.data["user_questions"], questions)
        self.assertEqual(self.strategy.data["user_answers"], answers)
        self.assertTrue("salt" in self.strategy.data)
        self.assertTrue("hashed_secret" in self.strategy.data)

    def test_register_empty_question(self):
        # Arrange
        questions = []
        answers = "blue"

        # Act
        result = self.strategy.register(questions, answers)

        # Assert
        self.assertFalse(result)
        self.assertFalse("timestamp_register" in self.strategy.data)
        self.assertFalse("user_questions" in self.strategy.data)
        self.assertFalse("user_answers" in self.strategy.data)
        self.assertFalse("salt" in self.strategy.data)
        self.assertFalse("hashed_secret" in self.strategy.data)

    def test_register_empty_answer(self):
        # Arrange
        questions = ["What is your favorite color?", "What is your pet's name?"]
        answers = ""

        # Act
        result = self.strategy.register(questions, answers)

        # Assert
        self.assertFalse(result)
        self.assertFalse("timestamp_register" in self.strategy.data)
        self.assertFalse("user_questions" in self.strategy.data)
        self.assertFalse("user_answers" in self.strategy.data)
        self.assertFalse("salt" in self.strategy.data)
        self.assertFalse("hashed_secret" in self.strategy.data)

    def test_authenticate(self):
        # Arrange
        questions = ["What is your favorite color?", "What is your pet's name?"]
        answers = "blue$dog"
        self.strategy.register(questions, answers)

        # Act
        result = self.strategy.authenticate(answers)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["answers"], answers)

    def test_authenticate_false(self):
        # Arrange
        questions = ["What is your favorite color?", "What is your pet's name?"]
        answers = "blue$dog"
        self.strategy.register(questions, answers)

        # Act
        result = self.strategy.authenticate("red$cat")

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["answers"], "red$cat")

    def test_bypass(self):
        # Arrange
        questions = ["What is your favorite color?", "What is your pet's name?"]
        answers = "blue$dog"
        self.strategy.register(questions, answers)

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["answers"], self.strategy.data["user_answers"])


class TestTwoFAKeyStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = TwoFAKeyStrategy()

    def test_get_type(self):
        self.assertEqual(self.strategy.get_type(), Method.TWOFA_KEY)

    def test_generate_challenge(self):
        # Act
        challenge = self.strategy.generate_challenge()

        # Assert
        self.assertIsInstance(challenge, bytes)
        self.assertEqual(len(challenge), 16)

    def test_register(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'

        # Act
        result = self.strategy.register(fingerprint)

        # Assert
        self.assertTrue(result)
        self.assertTrue("timestamp_register" in self.strategy.data)
        self.assertEqual(self.strategy.data["user_fingerprint"], fingerprint)
        self.assertEqual(self.strategy.data["fingerprint"], b"")
        self.assertTrue("fingerprint_template" in self.strategy.data)
        self.assertTrue("public_key" in self.strategy.data)
        self.assertTrue("private_key" in self.strategy.data)
        self.assertTrue("key_handle" in self.strategy.data)

    def test_register_false(self):
        # Arrange
        fingerprint = b''

        # Act
        result = self.strategy.register(fingerprint)

        # Assert
        self.assertFalse(result)
        self.assertFalse("timestamp_register" in self.strategy.data)
        self.assertFalse("user_fingerprint" in self.strategy.data)
        self.assertFalse("fingerprint" in self.strategy.data)
        self.assertFalse("fingerprint_template" in self.strategy.data)
        self.assertFalse("public_key" in self.strategy.data)
        self.assertFalse("private_key" in self.strategy.data)
        self.assertFalse("key_handle" in self.strategy.data)

    def test_authenticate(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        self.strategy.register(fingerprint)

        # Act
        result = self.strategy.authenticate(fingerprint)

        # Assert
        self.assertEqual(self.strategy.data["user_fingerprint"], fingerprint)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["fingerprint"], fingerprint)
        self.assertTrue("nonce" in self.strategy.data)
        self.assertTrue("signed_challenge" in self.strategy.data)

    def test_authenticate_false(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        false_fingerprint = b'\x01\x02\x03\x04\x06'
        self.strategy.register(fingerprint)

        # Act
        result = self.strategy.authenticate(false_fingerprint)

        # Assert
        self.assertFalse(result)
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["fingerprint"], false_fingerprint)
        self.assertFalse("nonce" in self.strategy.data)
        self.assertFalse("signed_challenge" in self.strategy.data)

    def test_bypass(self):
        # Arrange
        fingerprint = b'\x01\x02\x03\x04\x05'
        self.strategy.register(fingerprint)

        # Act
        self.strategy.bypass()

        # Assert
        self.assertTrue("timestamp_authenticate" in self.strategy.data)
        self.assertEqual(self.strategy.data["fingerprint"], self.strategy.data["user_fingerprint"])
        self.assertTrue("nonce" in self.strategy.data)
        self.assertTrue("signed_challenge" in self.strategy.data)