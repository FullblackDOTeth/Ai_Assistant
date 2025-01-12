import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

class Deployer:
    def __init__(self, environment: str):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / f'.env.{environment}'

    def validate_environment(self) -> None:
        """Validate environment configuration."""
        valid_envs = ['development', 'staging', 'production']
        if self.environment not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of: {', '.join(valid_envs)}")

    def load_env_file(self) -> None:
        """Load environment variables from .env file."""
        if not self.env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {self.env_file}")

        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    def run_migrations(self) -> None:
        """Run database migrations."""
        print(f"Running migrations for {self.environment}...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)

    def build_application(self) -> None:
        """Build the application."""
        print("Building application...")
        subprocess.run(["pyinstaller", "--onefile", "--windowed", 
                       "--name", "HeadAI", "src/main.py"], check=True)

    def run_tests(self) -> None:
        """Run tests before deployment."""
        print("Running tests...")
        result = subprocess.run(["pytest", "tests"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Tests failed:")
            print(result.stdout)
            print(result.stderr)
            raise Exception("Tests failed")

    def backup_database(self) -> None:
        """Backup database before deployment."""
        if self.environment in ['staging', 'production']:
            print("Backing up database...")
            timestamp = subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()
            backup_file = f"backup_{self.environment}_{timestamp}.sql"
            subprocess.run([
                "pg_dump",
                f"--file={backup_file}",
                "--format=custom",
                f"head_ai_{self.environment}"
            ], check=True)

    def deploy(self) -> None:
        """Main deployment process."""
        try:
            print(f"Starting deployment to {self.environment}...")
            
            # Validation steps
            self.validate_environment()
            self.load_env_file()
            
            # Pre-deployment steps
            if self.environment != 'development':
                self.run_tests()
                self.backup_database()
            
            # Deployment steps
            self.run_migrations()
            self.build_application()
            
            # Post-deployment steps
            self.update_configuration()
            self.restart_services()
            
            print(f"Deployment to {self.environment} completed successfully!")
            
        except Exception as e:
            print(f"Deployment failed: {str(e)}")
            sys.exit(1)

    def update_configuration(self) -> None:
        """Update configuration files."""
        config_dir = self.project_root / 'config' / 'environments'
        target_config = config_dir / f'{self.environment}.yml'
        
        if not target_config.exists():
            raise FileNotFoundError(f"Configuration file not found: {target_config}")
            
        # Copy configuration to deployment location
        subprocess.run([
            "cp",
            str(target_config),
            "/etc/headai/config.yml"
        ], check=True)

    def restart_services(self) -> None:
        """Restart application services."""
        if self.environment != 'development':
            print("Restarting services...")
            services = ['headai-web', 'headai-worker', 'headai-scheduler']
            for service in services:
                subprocess.run(["systemctl", "restart", service], check=True)

def main():
    parser = argparse.ArgumentParser(description='Deploy Head AI to specified environment')
    parser.add_argument('environment', choices=['development', 'staging', 'production'],
                       help='Target environment for deployment')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip running tests before deployment')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip database backup before deployment')
    
    args = parser.parse_args()
    
    deployer = Deployer(args.environment)
    deployer.deploy()

if __name__ == '__main__':
    main()
