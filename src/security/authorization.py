from typing import Dict, List, Optional, Set
from functools import wraps
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class Permission:
    name: str
    description: str
    resource: str
    actions: Set[str]

class AuthorizationManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize role-based permissions
        self.role_permissions: Dict[str, List[Permission]] = {
            'admin': [
                Permission('all', 'Full system access', '*', {'*'}),
            ],
            'manager': [
                Permission('user_manage', 'Manage users', 'user', {'create', 'read', 'update', 'delete'}),
                Permission('report_access', 'Access reports', 'report', {'read', 'create'}),
            ],
            'user': [
                Permission('user_read', 'Read user profile', 'user', {'read'}),
                Permission('report_read', 'Read reports', 'report', {'read'}),
            ]
        }
        
        # Cache for permission checks
        self._permission_cache: Dict[str, Dict] = {}
        
    def has_permission(self, user_role: str, resource: str, action: str) -> bool:
        """Check if user role has permission for action on resource."""
        # Check cache first
        cache_key = f"{user_role}:{resource}:{action}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]['has_permission']
            
        # Admin role has all permissions
        if user_role == 'admin':
            self._cache_permission(cache_key, True)
            return True
            
        # Get role permissions
        role_perms = self.role_permissions.get(user_role, [])
        
        # Check permissions
        has_permission = False
        for perm in role_perms:
            if (perm.resource == '*' or perm.resource == resource) and \
               (action in perm.actions or '*' in perm.actions):
                has_permission = True
                break
                
        self._cache_permission(cache_key, has_permission)
        return has_permission
        
    def _cache_permission(self, cache_key: str, has_permission: bool) -> None:
        """Cache permission check result."""
        self._permission_cache[cache_key] = {
            'has_permission': has_permission,
            'timestamp': datetime.now()
        }
        
    def clear_permission_cache(self) -> None:
        """Clear permission cache."""
        self._permission_cache.clear()
        
    def get_user_permissions(self, user_role: str) -> List[Permission]:
        """Get all permissions for a user role."""
        return self.role_permissions.get(user_role, [])
        
    def add_role_permission(self, role: str, permission: Permission) -> None:
        """Add a permission to a role."""
        if role not in self.role_permissions:
            self.role_permissions[role] = []
            
        self.role_permissions[role].append(permission)
        self.clear_permission_cache()
        
    def remove_role_permission(self, role: str, permission_name: str) -> None:
        """Remove a permission from a role."""
        if role in self.role_permissions:
            self.role_permissions[role] = [
                p for p in self.role_permissions[role]
                if p.name != permission_name
            ]
            self.clear_permission_cache()
            
def require_permission(resource: str, action: str):
    """Decorator to check permission for resource and action."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user role from context (implement based on your auth system)
            user_role = get_current_user_role()
            
            auth_manager = AuthorizationManager({})  # Get your config
            if not auth_manager.has_permission(user_role, resource, action):
                raise PermissionError(
                    f"User role '{user_role}' does not have permission "
                    f"for action '{action}' on resource '{resource}'"
                )
                
            return func(*args, **kwargs)
        return wrapper
    return decorator
    
def get_current_user_role() -> str:
    """Get current user's role from context."""
    # Implement based on your auth system
    pass
