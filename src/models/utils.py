import base64
import hashlib
import hmac

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


def encrypt_block(key, block, iv):
    # XOR the block with the IV
    block_xor_iv = bytes(a ^ b for a, b in zip(block, iv))

    # Hash the result using HMAC-SHA256
    hash_obj = hmac.new(key, block_xor_iv, hashlib.sha256)

    # Update the IV with the hash
    iv = hash_obj.digest()

    # Return the hash (the new IV) as the encrypted block
    return iv

def encrypt_images(image_dirs, key, iv):
    # Initialize an empty list to store encrypted image bytes
    encrypted_image_bytes = []

    # Iterate through each image directory
    for img_dir in image_dirs:
        # Open the image
        with open(img_dir, 'rb') as img_file:
            # Read the image file as bytes
            img_bytes = img_file.read()
        
        # Pad the image bytes to be a multiple of block size (32 bytes)
        img_bytes += b'\0' * (32 - len(img_bytes) % 32)

        # Encrypt the image bytes using CBC mode
        encrypted_img_bytes = b''

        # Split the image bytes into 32-byte blocks
        for i in range(0, len(img_bytes), 32):
            block = img_bytes[i:i+32]
            encrypted_block = encrypt_block(key, block, iv)
            encrypted_img_bytes += encrypted_block

        # Append the encrypted image bytes to the list
        encrypted_image_bytes.append(encrypted_img_bytes)

    # Combine the image bytes into a single byte string
    return b''.join(encrypted_image_bytes)