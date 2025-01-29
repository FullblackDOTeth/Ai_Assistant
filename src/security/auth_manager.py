import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
from dataclasses import dataclass

@dataclass
class User:
    id: str
    username: str
    email: str
    role: str
    password_hash: str
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

class AuthManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.jwt_secret = config['security']['jwt_secret']
        self.jwt_expiry = timedelta(hours=config['security']['jwt_expiry_hours'])
        self.max_failed_attempts = config['security'].get('max_failed_attempts', 5)
        self.lockout_duration = timedelta(minutes=config['security'].get('lockout_duration_minutes', 30))
        
        # In-memory session store (should be replaced with Redis in production)
        self._sessions: Dict[str, Dict] = {}
        
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> User:
        """Create a new user with hashed password."""
        # Generate unique user ID
        user_id = secrets.token_urlsafe(16)
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            password_hash=password_hash
        )
        
        self.logger.info(f"Created new user: {username}")
        return user
        
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Authenticate user and return (success, token, error_message)."""
        try:
            # Get user (implement your user storage)
            user = self._get_user_by_username(username)
            
            if not user:
                return False, None, "Invalid username or password"
                
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.now():
                return False, None, f"Account locked until {user.locked_until}"
                
            # Verify password
            if not self._verify_password(password, user.password_hash):
                user.failed_attempts += 1
                
                # Check if account should be locked
                if user.failed_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.now() + self.lockout_duration
                    self.logger.warning(f"Account locked for user: {username}")
                    return False, None, f"Account locked for {self.lockout_duration.minutes} minutes"
                
                return False, None, "Invalid username or password"
                
            # Reset failed attempts on successful login
            user.failed_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            
            # Generate token
            token = self._generate_token(user)
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            self._sessions[session_id] = {
                'user_id': user.id,
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            self.logger.info(f"Successful login for user: {username}")
            return True, token, None
            
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False, None, "Authentication error occurred"
            
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate JWT token and return (is_valid, payload, error_message)."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if token is expired
            exp = datetime.fromtimestamp(payload['exp'])
            if exp < datetime.now():
                return False, None, "Token expired"
                
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token expired"
        except jwt.InvalidTokenError:
            return False, None, "Invalid token"
            
    def refresh_token(self, token: str) -> Tuple[Optional[str], Optional[str]]:
        """Refresh JWT token and return (new_token, error_message)."""
        is_valid, payload, error = self.validate_token(token)
        
        if not is_valid:
            return None, error
            
        # Generate new token with updated expiry
        new_token = self._generate_token({
            'id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role']
        })
        
        return new_token, None
        
    def logout(self, session_id: str) -> None:
        """Logout user by invalidating their session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            self.logger.info(f"User logged out: {session_id}")
            
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
        
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode(), password_hash.encode())
        
    def _generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        now = datetime.now()
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'iat': now,
            'exp': now + self.jwt_expiry
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (implement your user storage)."""
        # This is a placeholder. Implement your user storage (database) logic
        pass
