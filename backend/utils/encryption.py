"""
Encryption utilities for sensitive data
Uses Fernet symmetric encryption from cryptography library
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption/decryption of sensitive data"""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize encryption manager

        Args:
            secret_key: Base secret key for deriving encryption key.
                       If None, uses SECRET_KEY from environment.
        """
        if secret_key is None:
            secret_key = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")

        # Derive a Fernet key from the secret
        self.fernet_key = self._derive_fernet_key(secret_key)
        self.cipher = Fernet(self.fernet_key)

    def _derive_fernet_key(self, secret: str) -> bytes:
        """
        Derive a Fernet-compatible key from the secret

        Args:
            secret: Base secret string

        Returns:
            32-byte Fernet key
        """
        # Use PBKDF2HMAC to derive a 32-byte key from the secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"autocbot_salt_v1",  # Fixed salt for deterministic key derivation
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return key

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value

        Args:
            plaintext: Plain text to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""

        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string value

        Args:
            ciphertext: Encrypted text to decrypt

        Returns:
            Decrypted plain text
        """
        if not ciphertext:
            return ""

        try:
            decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_value(value: str) -> str:
    """Convenience function to encrypt a value"""
    return get_encryption_manager().encrypt(value)


def decrypt_value(value: str) -> str:
    """Convenience function to decrypt a value"""
    return get_encryption_manager().decrypt(value)
