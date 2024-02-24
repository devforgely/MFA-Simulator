import secrets

# For purpose of simulation, the protocol is simplified

class DiffieHellmanProtocol:
    def __init__(self, g=2, p=23):
        self.g = g # Random integer 1<g<n (dont need to be secret)
        self.n = p # Large prime number (dont need to be secret)

        self.a = secrets.randbelow(self.n) # A's private key
        self.b = secrets.randbelow(self.n) # B's private key

    def exchange_keys(self):
        # A and B exchange public keys
        self.A = (self.g**self.a) % self.n  # A's public key
        self.B = (self.g**self.b) % self.n  # B's public key

    def compute_shared_secret(self) -> int:
        # They both compute the shared secret
        s_A = (self.B**self.a) % self.n
        s_B = (self.A**self.b) % self.n

        assert s_A == s_B  # The shared secrets should be equal

        return s_A  # Return the shared secret
    


