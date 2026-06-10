"""
Encryption service stub.
Provides Fernet symmetric encryption for sensitive user credentials
(e.g., job board passwords stored for auto-apply).
"""


def encrypt(plaintext: str) -> str:
    """
    Stub: Encrypt a plaintext string using the FERNET_KEY from settings.
    Returns the base64-encoded ciphertext.
    """
    raise NotImplementedError("encryption_service.encrypt is not implemented yet.")


def decrypt(ciphertext: str) -> str:
    """
    Stub: Decrypt a Fernet-encrypted ciphertext string.
    Returns the original plaintext.
    """
    raise NotImplementedError("encryption_service.decrypt is not implemented yet.")
