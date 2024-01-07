## Pin Authentication

1. PIN Creation: The user creates a PIN on their device.
2. Asymmetric Key Pair Generation: The system generates an asymmetric key pair. This consists of a private key, which is kept secret on the user's device, and a public key, which is registered with the identity provider.
3. Trusted Relationship Establishment: The registration of the public key with the identity provider establishes a trusted relationship. The identity provider now recognizes the public key as a valid identifier for the user.

---

## Pin Registeration

4. Authentication Key Unlocking: When the user enters their PIN, the system unlocks the authentication key (the private key of the asymmetric key pair)
5. Request Signing: The unlocked key is used to sign the request that is sent to the authenticating server.
6. Server Verification: The server verifies the signed request using the public key. If the verification is successful, the user is authenticated.

The processes ensures that the PIN is local to the device, never transmitted anywhere, and isn't stored on the server. It's important to note that the PIN is tied to the specific device on which it was set up, making it useless to anyone without that specific hardware. This means that even if someone obtains your PIN, they'd have to also have access to your device.