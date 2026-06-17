"""
Fernet symmetric encryption service.

Used to encrypt/decrypt sensitive user credentials (job-board usernames
and passwords) before storing them in the board_credentials table.

The module exposes a lazy-initialised singleton via `get_encryption_service()`.
"""

from cryptography.fernet import Fernet

from app.config import settings


class EncryptionService:
    def __init__(self, key: bytes) -> None:
        self.f = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Return base64-URL Fernet token for *plaintext*."""
        return self.f.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a Fernet token and return the original plaintext."""
        return self.f.decrypt(ciphertext.encode()).decode()


_instance: EncryptionService | None = None


def get_encryption_service() -> EncryptionService:
    """Return the module-level EncryptionService singleton, initialised lazily."""
    global _instance
    if _instance is None:
        if not settings.fernet_key:
            raise RuntimeError(
                "FERNET_KEY is not configured. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        _instance = EncryptionService(settings.fernet_key.encode())
    return _instance
