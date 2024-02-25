import string
import base64

def normalise_text(text: str) -> str:
    # only include lower case alphabet and number (no punctuation, no space)
    text = ''.join(char for char in text if char.isalnum())
    return text.lower()

def parse_array(arr: list[str]) -> str:
    return "\n".join(arr)

def byte_str(bytes_val: bytes) -> str:
    return base64.b64encode(bytes_val).decode('utf-8')

def calculate_security_level(text: str) -> int:
    score = 0

    # Check for length
    if len(text) > 15:
        score += 40
    elif len(text) >= 8:
        score += 20
    elif len(text) >= 6:
        score += 10
    
    if any(c in string.ascii_lowercase for c in text):
        score += 10
    
    if any(c in string.ascii_uppercase for c in text):
        score += 15
    
    if any(c.isdigit() for c in text):
        score += 12

    if any(c in string.punctuation for c in text):
        score += 15

    return score

def image_byte(image_dir):
    with open(image_dir, 'rb') as img_file:
        # Read the image file as bytes
        img_bytes = img_file.read()
    return img_bytes

def images_to_bytes(image_dirs):
    # Initialize an empty list to store image bytes
    image_bytes = []

    # Iterate through each image directory
    for img_dir in image_dirs:
        # Open the image
        with open(img_dir, 'rb') as img_file:
            # Read the image file as bytes
            img_bytes = img_file.read()
        
        # Append the image bytes to the list
        image_bytes.append(img_bytes)

    # Combine the image bytes into a single byte string
    combined_bytes = b''.join(image_bytes)

    return combined_bytes