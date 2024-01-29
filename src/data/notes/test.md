## <span style="color:blue;">Pin Authentication</span>

1. <span style="font-size:14px;">PIN Creation: The user creates a PIN on their device.</span>
2. <span style="font-size:14px;">Asymmetric Key Pair Generation: The system generates an asymmetric key pair. This consists of a private key, which is kept secret on the user's device, and a public key, which is registered with the identity provider.</span>
3. <span style="font-size:14px;">Trusted Relationship Establishment: The registration of the public key with the identity provider establishes a trusted relationship. The identity provider now recognizes the public key as a valid identifier for the user.</span>

---

## <span style="color:green;">Pin Registration</span>

4. <span style="font-size:14px;">Authentication Key Unlocking: When the user enters their PIN, the system unlocks the authentication key (the private key of the asymmetric key pair).</span>
5. <span style="font-size:14px;">Request Signing: The unlocked key is used to sign the request that is sent to the authenticating server.</span>
6. <span style="font-size:14px;">Server Verification: The server verifies the signed request using the public key. If the verification is successful, the user is authenticated.</span>

The processes ensures that the PIN is local to the device, never transmitted anywhere, and isn't stored on the server. It's important to note that the PIN is tied to the specific device on which it was set up, making it useless to anyone without that specific hardware. This means that even if someone obtains your PIN, they'd have to also have access to your device.

<img src="resources\images\coin.png" alt="coin" width="300" height="300"><img src="resources\images\coin.png" alt="coin">

<blockquote cite="https://www.example.com">
    This is a blockquote. It's used to indicate the quotation of a large section of text from another source.
</blockquote>

<cite>This is a citation.</cite>

<abbr title="Hypertext Markup Language">HTML</abbr> is the standard markup language for documents designed to be displayed in a web browser.

<acronym title="As Soon As Possible">ASAP</acronym>

<samp>This text is a sample output from a computer program.</samp>

<dfn title="The definition title goes here.">This is a term that is being defined.</dfn>

<img src="resources\images\coin.png" alt="coin">