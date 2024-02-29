# Use of Biometrics

<span>The use of biometrics (something you are) in authentication includes both measurement of physical characteristics (e.g., fingerprint, iris, facial characteristics) and behavioral characteristics (e.g., typing cadence).</span>

---

## Disadvantage of biometric as form of authentication

- The biometric False Match Rate (FMR) does not provide confidence in the authentication of the subscriber by itself. In addition, FMR does not account for spoofing attacks.

- Biometric comparison is probabilistic, whereas the other authentication factors are deterministic.

- Biometric template protection schemes provide a method for revoking biometric credentials that is comparable to other authentication factors (e.g., PKI certificates and passwords). However, the availability of such solutions is limited, and standards for testing these methods are under development.

- Biometric characteristics do not constitute secrets. They can be obtained online or by taking a picture of someone with a camera phone (e.g., facial images) with or without their knowledge, lifted from objects someone touches (e.g., latent fingerprints), or captured with high resolution images (e.g., iris patterns). While presentation attack detection (PAD) technologies (e.g., liveness detection) can mitigate the risk of these types of attacks, additional trust in the sensor or biometric processing is required to ensure that PAD is operating in accordance with the needs of the Credential Service Provider (CSP) and the subscriber.

---

## Biometric system guidelines

Biometrics SHALL be used only as part of multi-factor authentication with a physical authenticator (something you have).

An authenticated protected channel between sensor (or an endpoint containing a sensor that resists sensor replacement) and verifier SHALL be established and the sensor or endpoint SHALL be authenticated prior to capturing the biometric sample from the claimant.

The biometric system SHALL operate with an FMR of 1 in 1000 or better. This FMR SHALL be achieved under conditions of a conformant attack (i.e., zero-effort impostor attempt).

The biometric system SHOULD implement PAD. Testing of the biometric system to be deployed SHOULD demonstrate at least 90% resistance to presentation attacks for each relevant attack type (i.e., species), where resistance is defined as the number of thwarted presentation attacks divided by the number of trial presentation attacks. The PAD decision MAY be made either locally on the claimant's device or by a central verifier.

<dfn>Presentation Attack Detection (PAD) it is the process of detecting a biometric spoof, also known as a presentation attack. These attacks can subvert a biometric system by using tools called presentation attack instruments (PAIs), such as photographs, masks, fake silicone fingerprints, or even video replays.</dfn>

PAD systems utilize a combination of hardware and software technologies to determine whether or not a presented biometric is genuine. A subset of this is liveness detection, which refers to a PAD system's specific ability to differentiate between human beings and non-living spoofs.

PAD is crucial in applications where the combination of security and convenience is a priority. This is especially true in automated identification and authentication scenarios - such as physical access control, travel facilitation, payments, or online identity verification