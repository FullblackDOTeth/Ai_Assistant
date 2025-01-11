"""
Cryptography and blockchain plugin
"""

from . import Plugin
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json
from typing import Dict, Any

class CryptoPlugin(Plugin):
    def __init__(self):
        self._name = "crypto"
        self._description = "Cryptography and blockchain capabilities"
        self._key = None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def initialize(self) -> None:
        """Initialize cryptographic components"""
        # Generate RSA key pair
        self._key = RSA.generate(2048)
        print(f"Initialized {self.name} plugin")
    
    def execute(self, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute cryptographic operations"""
        if action == "hash":
            return self._hash_data(data)
        elif action == "encrypt":
            return self._encrypt_data(data)
        elif action == "decrypt":
            return self._decrypt_data(data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _hash_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create SHA256 hash of data"""
        hasher = SHA256.new()
        hasher.update(json.dumps(data).encode())
        return {
            "hash": hasher.hexdigest(),
            "algorithm": "SHA256"
        }
    
    def _encrypt_data(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        """Encrypt data using RSA"""
        cipher = PKCS1_OAEP.new(self._key.publickey())
        encrypted = cipher.encrypt(json.dumps(data).encode())
        return {
            "encrypted": encrypted,
            "public_key": self._key.publickey().export_key()
        }
    
    def _decrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt data using RSA"""
        cipher = PKCS1_OAEP.new(self._key)
        decrypted = cipher.decrypt(data["encrypted"])
        return json.loads(decrypted.decode())
