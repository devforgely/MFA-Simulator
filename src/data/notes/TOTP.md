## Time-based One-Time Password


Generate 16-character, base32-encoded seed
The current time must be hashed together with the shared key to make the passcode constantly change the hash digest.
The protocol establishes a time step (default value of 30s) for the passcode to be updated.
The number of time steps T is hashed together with the seed.
The RFC6238 protocol uses HMAC-SHA-1 by default.

As specified in RFC 4226, we first look at the last character of the hash to determine a starting point for our truncated hash.
For example So we grab the next 31 bits, starting with offset 1 on SHA-1 Hash (9acf2f7d742997c8e39912959a1cf4fc12f28261)
Truncated value from the original hash is cf2f7d74. To get the TOTP we just have to convert it to decimal and show the last d digits by calculating the modulo 10^d of the string.