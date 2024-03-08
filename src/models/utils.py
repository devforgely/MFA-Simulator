import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad



def normalise_text(text: str) -> str:
    # only include lower case alphabet and number (no punctuation, no space)
    text = ''.join(char for char in text if char.isalnum())
    return text.lower()

def parse_array(arr: list[str]) -> str:
    return "\n".join(arr)

def byte_str(bytes_val: bytes) -> str:
    return base64.b64encode(bytes_val).decode('utf-8')

def decode_key(key) -> str:
    return key.save_pkcs1().decode()

def image_byte(image_dir: str):
    with open(image_dir, 'rb') as img_file:
        # Read the image file as bytes
        img_bytes = img_file.read()
    return img_bytes

def encrypt_images(image_dirs, key, iv):
    # Initialize an empty list to store encrypted image bytes
    encrypted_images = []

    # Iterate through each image directory
    for img_dir in image_dirs:
        # Open the image
        with open(img_dir, 'rb') as img_file:
            # Read the image file as bytes
            img_bytes = img_file.read()

        # Pad the image bytes to be a multiple of block size (16 bytes for AES)
        img_bytes = pad(img_bytes, 16)

        # Create a new AES cipher object
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Encrypt the image bytes using CBC mode
        encrypted_img_bytes = cipher.encrypt(img_bytes)

        # Append the encrypted image bytes to the list
        encrypted_images.append(encrypted_img_bytes)

    # Return the list of encrypted image bytes
    return encrypted_images

def decrypt_images(encrypted_images, key, iv):
    # Initialize an empty list to store decrypted image bytes
    decrypted_images = []

    # Iterate through each encrypted image
    for encrypted_img_bytes in encrypted_images:
        # Create a new AES cipher object
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt the image bytes using CBC mode
        decrypted_img_bytes = cipher.decrypt(encrypted_img_bytes)

        # Unpad the decrypted image bytes
        decrypted_img_bytes = unpad(decrypted_img_bytes, 16)

        # Append the decrypted image bytes to the list
        decrypted_images.append(decrypted_img_bytes)

    # Return the list of decrypted image bytes
    return decrypted_images