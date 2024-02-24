import base64
import string

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