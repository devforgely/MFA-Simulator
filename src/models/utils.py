from models.authentication.authentication import Method

def normalise_text(text: str) -> str:
    # only include lower case alphabet and number (no punctuation, no space)
    text = ''.join(char for char in text if char.isalnum())
    return text.lower()

def calculate_assurance_level(methods: list[Method]) -> str:
    if len(methods) == 0: return ""

    level_one = """Authenticator Assurance Level 1|AAL1 provides some assurance that the claimant controls an authenticator bound to the subscriber's account. AAL1 requires either single-factor or multi-factor authentication using a wide range of available authentication technologies. Successful authentication requires that the claimant prove possession and control of the authenticator through a secure authentication protocol."""
    
    level_two = """Authenticator Assurance Level 2|AAL2 provides high confidence that the claimant controls an authenticator(s) bound to the subscriber's account. Proof of possession and control of two different authentication factors is required through secure authentication protocol(s). Approved cryptographic techniques are required at AAL2 and above."""
    
    level_three = """Authenticator Assurance Level 3|AAL3 provides very high confidence that the claimant controls authenticator(s) bound to the subscriber's account. Authentication at AAL3 is based on proof of possession of a key through a cryptographic protocol. AAL3 authentication requires a hardware-based authenticator and an authenticator that provides verifier impersonation resistance; the same device may fulfill both these requirements. In order to authenticate at AAL3, claimants are required to prove possession and control of two distinct authentication factors through secure authentication protocol(s). Approved cryptographic techniques are required."""

    knowledge_based = {Method.PASSWORD, Method.PIN, Method.SECRET_QUESTION, Method.IMAGE_PASSWORD}
    biometric_based = {Method.FINGER_PRINT}
    possession_based = {Method.PUSH_NOTIFICATION}

    if Method.TWOFA_KEY in methods:
        return level_three
    elif any(element in knowledge_based for element in methods) \
        + any(element in biometric_based for element in methods) \
        + any(element in possession_based for element in methods) >= 2:
        return level_two
    return level_one
