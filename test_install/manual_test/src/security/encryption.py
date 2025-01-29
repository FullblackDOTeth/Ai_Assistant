from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Dict, Optional, Tuple
import logging

class EncryptionManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption keys
        self.data_key = self._generate_or_load_key('data_encryption_key')
        self.fernet = Fernet(self.data_key)
        
    def _generate_or_load_key(self, key_name: str) -> bytes:
        """Generate or load encryption key."""
        key_path = self.config['security'].get('key_path', 'keys')
        key_file = os.path.join(key_path, f"{key_name}.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return base64.urlsafe_b64decode(f.read())
                
        # Generate new key
        key = Fernet.generate_key()
        
        # Ensure directory exists
        os.makedirs(key_path, exist_ok=True)
        
        # Save key
        with open(key_file, 'wb') as f:
            f.write(base64.urlsafe_b64encode(key))
            
        return key
        
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt binary data."""
        try:
            return self.fernet.encrypt(data)
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            raise
            
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data."""
        try:
            return self.fernet.decrypt(encrypted_data)
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            raise
            
    def encrypt_string(self, text: str) -> str:
        """Encrypt string data."""
        try:
            encrypted_data = self.encrypt_data(text.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"String encryption error: {str(e)}")
            raise
            
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt string data."""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_data = self.decrypt_data(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"String decryption error: {str(e)}")
            raise
            
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generate a new encryption key pair."""
        try:
            private_key = os.urandom(32)
            public_key = self.derive_public_key(private_key)
            return private_key, public_key
        except Exception as e:
            self.logger.error(f"Key pair generation error: {str(e)}")
            raise
            
    def derive_public_key(self, private_key: bytes) -> bytes:
        """Derive public key from private key."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'headai_key_derivation',
                iterations=100000,
                backend=default_backend()
            )
            return base64.urlsafe_b64encode(kdf.derive(private_key))
        except Exception as e:
            self.logger.error(f"Key derivation error: {str(e)}")
            raise
            
    def rotate_keys(self) -> None:
        """Rotate encryption keys."""
        try:
            # Generate new key
            new_key = Fernet.generate_key()
            new_fernet = Fernet(new_key)
            
            # Re-encrypt all data with new key (implement based on your storage)
            self._reencrypt_data(new_fernet)
            
            # Update current key
            self.data_key = new_key
            self.fernet = new_fernet
            
            # Save new key
            key_path = self.config['security'].get('key_path', 'keys')
            with open(os.path.join(key_path, 'data_encryption_key.key'), 'wb') as f:
                f.write(base64.urlsafe_b64encode(new_key))
                
            self.logger.info("Encryption keys rotated successfully")
            
        except Exception as e:
            self.logger.error(f"Key rotation error: {str(e)}")
            raise
            
    def _reencrypt_data(self, new_fernet: Fernet) -> None:
        """Re-encrypt all data with new key."""
        # Implement based on your data storage
        pass
        
class FileEncryption:
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.logger = logging.getLogger(__name__)
        
    def encrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file."""
        try:
            if output_path is None:
                output_path = input_path + '.encrypted'
                
            with open(input_path, 'rb') as f:
                data = f.read()
                
            encrypted_data = self.encryption_manager.encrypt_data(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
                
            return output_path
            
        except Exception as e:
            self.logger.error(f"File encryption error: {str(e)}")
            raise
            
    def decrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file."""
        try:
            if output_path is None:
                output_path = input_path.replace('.encrypted', '')
                
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.encryption_manager.decrypt_data(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
                
            return output_path
            
        except Exception as e:
            self.logger.error(f"File decryption error: {str(e)}")
            raise
