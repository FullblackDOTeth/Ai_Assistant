import os
import yaml
from typing import Dict, Any
from pathlib import Path

class ConfigLoader:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env = os.getenv('HEADAI_ENV', 'development')
        self.config_dir = Path(__file__).parent.parent.parent / 'config'

    def load_config(self) -> Dict[str, Any]:
        """Load configuration based on current environment."""
        config_path = self.config_dir / 'environments' / f'{self.env}.yml'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Override with environment variables
        self._override_from_env(self.config)
        
        return self.config

    def _override_from_env(self, config: Dict[str, Any], prefix: str = '') -> None:
        """Recursively override configuration values with environment variables."""
        for key, value in config.items():
            env_key = f"{prefix}_{key}".upper().strip('_')
            
            if isinstance(value, dict):
                self._override_from_env(value, env_key)
            else:
                env_value = os.getenv(env_key)
                if env_value is not None:
                    # Convert environment variable to appropriate type
                    if isinstance(value, bool):
                        config[key] = env_value.lower() in ('true', '1', 'yes')
                    elif isinstance(value, int):
                        config[key] = int(env_value)
                    elif isinstance(value, float):
                        config[key] = float(env_value)
                    else:
                        config[key] = env_value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self.env == 'production'

    @property
    def is_staging(self) -> bool:
        """Check if current environment is staging."""
        return self.env == 'staging'

    @property
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self.env == 'development'
