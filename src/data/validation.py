from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel, ValidationError, validator
import re
import logging
from datetime import datetime

class ValidationError(Exception):
    def __init__(self, message: str, errors: List[Dict] = None):
        super().__init__(message)
        self.errors = errors or []

class DataValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_model(self, data: Dict, model_class: Type[BaseModel]) -> Dict:
        """Validate data against a Pydantic model."""
        try:
            validated_data = model_class(**data)
            return validated_data.dict()
        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise ValidationError(
                "Data validation failed",
                errors=e.errors()
            )
            
    def validate_type(self, value: Any, expected_type: Type) -> bool:
        """Validate value type."""
        return isinstance(value, expected_type)
        
    def validate_required_fields(self, data: Dict,
                               required_fields: List[str]) -> List[str]:
        """Validate required fields are present and not empty."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
            elif isinstance(data[field], str) and not data[field].strip():
                missing_fields.append(field)
        return missing_fields
        
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        min_length = 8
        requires_upper = True
        requires_lower = True
        requires_digit = True
        requires_special = True
        
        errors = []
        
        if len(password) < min_length:
            errors.append(f"Password must be at least {min_length} characters")
            
        if requires_upper and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
            
        if requires_lower and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
            
        if requires_digit and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
            
        if requires_special and not any(not c.isalnum() for c in password):
            errors.append("Password must contain at least one special character")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
        
    def validate_date_range(self, start_date: datetime,
                          end_date: datetime) -> bool:
        """Validate date range."""
        return start_date < end_date
        
    def validate_numeric_range(self, value: float,
                             min_value: Optional[float] = None,
                             max_value: Optional[float] = None) -> bool:
        """Validate numeric value within range."""
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True
        
    def validate_string_length(self, value: str,
                             min_length: Optional[int] = None,
                             max_length: Optional[int] = None) -> bool:
        """Validate string length within range."""
        length = len(value)
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
        
    def validate_list_length(self, value: List,
                           min_length: Optional[int] = None,
                           max_length: Optional[int] = None) -> bool:
        """Validate list length within range."""
        length = len(value)
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
        
    def validate_allowed_values(self, value: Any,
                              allowed_values: List[Any]) -> bool:
        """Validate value is in allowed values."""
        return value in allowed_values
        
    def validate_regex_pattern(self, value: str, pattern: str) -> bool:
        """Validate string matches regex pattern."""
        return bool(re.match(pattern, value))
        
# Example Pydantic models for validation
class UserModel(BaseModel):
    username: str
    email: str
    password: str
    role: str = 'user'
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
        
    @validator('email')
    def email_valid(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v
        
    @validator('password')
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(not c.isalnum() for c in v):
            raise ValueError('Password must contain special character')
        return v
        
class ProjectModel(BaseModel):
    name: str
    description: Optional[str]
    owner_id: str
    settings: Optional[Dict]
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v
        
class DatasetModel(BaseModel):
    name: str
    project_id: str
    file_path: str
    file_size: int
    metadata: Optional[Dict]
    
    @validator('file_size')
    def file_size_positive(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        return v
        
class ModelModel(BaseModel):
    name: str
    project_id: str
    type: str
    version: str
    file_path: str
    parameters: Optional[Dict]
    metrics: Optional[Dict]
    
    @validator('version')
    def version_format(cls, v):
        pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid version format (should be x.y.z)')
        return v
