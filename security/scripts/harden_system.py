#!/usr/bin/env python3

import os
import sys
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any

class SystemHardener:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.success_count = 0
        self.failure_count = 0

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_hardening.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('SecurityHardening')

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def harden_file_permissions(self) -> None:
        """Set secure file permissions for sensitive files."""
        sensitive_paths = [
            'security/config',
            'src/data',
            '.env',
            'security/keys'
        ]

        for path in sensitive_paths:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        os.chmod(path, 0o600)  # rw-------
                    else:
                        os.chmod(path, 0o700)  # rwx------
                    self.logger.info(f"Secured permissions for {path}")
                    self.success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to secure {path}: {e}")
                self.failure_count += 1

    def configure_network_security(self) -> None:
        """Configure network security settings."""
        try:
            network_config = self.config['security']['network']
            
            # Configure firewall rules
            if network_config['firewall']['enabled']:
                rules = network_config['firewall']['rules']
                for rule in rules:
                    cmd = f"netsh advfirewall firewall add rule"
                    cmd += f" name=\"HeadAI {rule['port']}\""
                    cmd += f" dir=in action={rule['action']}"
                    cmd += f" protocol=TCP localport={rule['port']}"
                    
                    subprocess.run(cmd, shell=True, check=True)
                
                self.logger.info("Firewall rules configured successfully")
                self.success_count += 1
        except Exception as e:
            self.logger.error(f"Failed to configure network security: {e}")
            self.failure_count += 1

    def setup_encryption(self) -> None:
        """Set up encryption keys and configurations."""
        try:
            encryption_config = self.config['security']['encryption']
            key_size = encryption_config['key_size']
            
            # Generate encryption keys
            key_path = Path('security/keys')
            key_path.mkdir(parents=True, exist_ok=True)
            
            # Generate main encryption key
            if not (key_path / 'master.key').exists():
                subprocess.run(
                    f"openssl rand -out {key_path}/master.key {key_size//8}",
                    shell=True, check=True
                )
            
            # Generate JWT keys
            if not (key_path / 'jwt-private.pem').exists():
                subprocess.run(
                    "openssl genpkey -algorithm RSA -out security/keys/jwt-private.pem -pkeyopt rsa_keygen_bits:2048",
                    shell=True, check=True
                )
                subprocess.run(
                    "openssl rsa -pubout -in security/keys/jwt-private.pem -out security/keys/jwt-public.pem",
                    shell=True, check=True
                )
            
            self.logger.info("Encryption keys generated successfully")
            self.success_count += 1
        except Exception as e:
            self.logger.error(f"Failed to setup encryption: {e}")
            self.failure_count += 1

    def configure_audit_logging(self) -> None:
        """Configure audit logging settings."""
        try:
            audit_config = self.config['security']['audit']
            log_path = Path('logs/audit')
            log_path.mkdir(parents=True, exist_ok=True)
            
            # Configure log rotation
            logrotate_config = f"""
            /var/log/headai/audit/*.log {{
                daily
                rotate {audit_config['retention_days']}
                compress
                delaycompress
                missingok
                notifempty
                create 0600 headai headai
            }}
            """
            
            with open('/etc/logrotate.d/headai-audit', 'w') as f:
                f.write(logrotate_config)
            
            self.logger.info("Audit logging configured successfully")
            self.success_count += 1
        except Exception as e:
            self.logger.error(f"Failed to configure audit logging: {e}")
            self.failure_count += 1

    def setup_access_control(self) -> None:
        """Configure role-based access control."""
        try:
            access_config = self.config['security']['access_control']
            
            # Create role definitions
            roles_path = Path('security/roles')
            roles_path.mkdir(parents=True, exist_ok=True)
            
            for role, settings in access_config['roles'].items():
                role_file = roles_path / f"{role}.yml"
                with open(role_file, 'w') as f:
                    yaml.dump({role: settings}, f)
            
            self.logger.info("Access control configured successfully")
            self.success_count += 1
        except Exception as e:
            self.logger.error(f"Failed to setup access control: {e}")
            self.failure_count += 1

    def configure_security_headers(self) -> None:
        """Configure security headers for the web application."""
        try:
            headers = self.config['security']['api_security']['security_headers']
            nginx_config = "server {\n"
            
            for header in headers:
                for name, value in header.items():
                    nginx_config += f"    add_header {name} {value} always;\n"
            
            nginx_config += "}\n"
            
            with open('security/nginx/security_headers.conf', 'w') as f:
                f.write(nginx_config)
            
            self.logger.info("Security headers configured successfully")
            self.success_count += 1
        except Exception as e:
            self.logger.error(f"Failed to configure security headers: {e}")
            self.failure_count += 1

    def run_vulnerability_scan(self) -> None:
        """Run vulnerability scanning tools."""
        try:
            scan_config = self.config['security']['vulnerability_scan']
            
            if scan_config['enabled']:
                # Run dependency check
                subprocess.run(
                    "safety check",
                    shell=True, check=True
                )
                
                # Run container scan
                subprocess.run(
                    "trivy filesystem .",
                    shell=True, check=True
                )
                
                # Run SAST analysis
                subprocess.run(
                    "bandit -r src/",
                    shell=True, check=True
                )
            
            self.logger.info("Vulnerability scan completed successfully")
            self.success_count += 1
        except Exception as e:
            self.logger.error(f"Failed to run vulnerability scan: {e}")
            self.failure_count += 1

    def harden_system(self) -> None:
        """Run all system hardening tasks."""
        self.logger.info("Starting system hardening process...")
        
        tasks = [
            self.harden_file_permissions,
            self.configure_network_security,
            self.setup_encryption,
            self.configure_audit_logging,
            self.setup_access_control,
            self.configure_security_headers,
            self.run_vulnerability_scan
        ]
        
        for task in tasks:
            task()
        
        self.logger.info(f"""
        System hardening completed:
        - Successful tasks: {self.success_count}
        - Failed tasks: {self.failure_count}
        Check security_hardening.log for details.
        """)

def main():
    if len(sys.argv) != 2:
        print("Usage: python harden_system.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    hardener = SystemHardener(config_path)
    hardener.harden_system()

if __name__ == "__main__":
    main()
