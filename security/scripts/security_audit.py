#!/usr/bin/env python3

import os
import sys
import json
import yaml
import datetime
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

class SecurityAuditor:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.report_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'issues': [],
            'recommendations': []
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_audit.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('SecurityAudit')

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def check_file_permissions(self) -> None:
        """Check file permissions for sensitive files."""
        sensitive_files = [
            ('security/config/security.yml', 0o600),
            ('security/keys', 0o700),
            ('.env', 0o600),
            ('src/data', 0o700)
        ]

        for file_path, expected_mode in sensitive_files:
            if os.path.exists(file_path):
                current_mode = os.stat(file_path).st_mode & 0o777
                if current_mode != expected_mode:
                    self.report_data['issues'].append({
                        'type': 'file_permission',
                        'severity': 'HIGH',
                        'description': f"Incorrect permissions on {file_path}",
                        'details': f"Current: {oct(current_mode)}, Expected: {oct(expected_mode)}"
                    })

    def audit_network_security(self) -> None:
        """Audit network security configuration."""
        try:
            # Check open ports
            result = subprocess.run(
                "netstat -tuln",
                shell=True, capture_output=True, text=True
            )
            
            open_ports = []
            for line in result.stdout.splitlines():
                if 'LISTEN' in line:
                    open_ports.append(line.split()[3].split(':')[-1])
            
            allowed_ports = [
                rule['port'] 
                for rule in self.config['security']['network']['firewall']['rules']
            ]
            
            for port in open_ports:
                if port not in allowed_ports:
                    self.report_data['issues'].append({
                        'type': 'network_security',
                        'severity': 'HIGH',
                        'description': f"Unauthorized open port: {port}",
                        'details': "Port not defined in firewall rules"
                    })
        except Exception as e:
            self.logger.error(f"Failed to audit network security: {e}")

    def check_encryption_configuration(self) -> None:
        """Audit encryption configuration and key management."""
        encryption_config = self.config['security']['encryption']
        key_path = Path('security/keys')
        
        # Check key existence and age
        key_files = ['master.key', 'jwt-private.pem', 'jwt-public.pem']
        for key_file in key_files:
            file_path = key_path / key_file
            if not file_path.exists():
                self.report_data['issues'].append({
                    'type': 'encryption',
                    'severity': 'CRITICAL',
                    'description': f"Missing encryption key: {key_file}",
                    'details': "Required encryption key not found"
                })
            else:
                key_age = datetime.datetime.now().timestamp() - file_path.stat().st_mtime
                if key_age > encryption_config['rotation_period_days'] * 86400:
                    self.report_data['issues'].append({
                        'type': 'encryption',
                        'severity': 'MEDIUM',
                        'description': f"Encryption key rotation needed: {key_file}",
                        'details': f"Key is {key_age/86400:.1f} days old"
                    })

    def audit_access_control(self) -> None:
        """Audit access control configuration."""
        access_config = self.config['security']['access_control']
        
        # Check role definitions
        roles_path = Path('security/roles')
        for role, settings in access_config['roles'].items():
            role_file = roles_path / f"{role}.yml"
            
            if not role_file.exists():
                self.report_data['issues'].append({
                    'type': 'access_control',
                    'severity': 'HIGH',
                    'description': f"Missing role definition: {role}",
                    'details': "Role configuration file not found"
                })
            else:
                with open(role_file) as f:
                    role_config = yaml.safe_load(f)
                    if role not in role_config:
                        self.report_data['issues'].append({
                            'type': 'access_control',
                            'severity': 'MEDIUM',
                            'description': f"Invalid role configuration: {role}",
                            'details': "Role configuration format is incorrect"
                        })

    def check_security_headers(self) -> None:
        """Audit security headers configuration."""
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': None
        }
        
        nginx_config_path = Path('security/nginx/security_headers.conf')
        if not nginx_config_path.exists():
            self.report_data['issues'].append({
                'type': 'security_headers',
                'severity': 'HIGH',
                'description': "Missing security headers configuration",
                'details': "Nginx security headers configuration not found"
            })
        else:
            with open(nginx_config_path) as f:
                config_content = f.read()
                for header, value in required_headers.items():
                    if header not in config_content:
                        self.report_data['issues'].append({
                            'type': 'security_headers',
                            'severity': 'MEDIUM',
                            'description': f"Missing security header: {header}",
                            'details': "Required security header not configured"
                        })

    def analyze_dependencies(self) -> None:
        """Analyze dependencies for known vulnerabilities."""
        try:
            # Run safety check
            result = subprocess.run(
                "safety check",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode != 0:
                vulnerabilities = result.stdout.strip().split('\n')
                for vuln in vulnerabilities:
                    self.report_data['issues'].append({
                        'type': 'dependency',
                        'severity': 'HIGH',
                        'description': "Vulnerable dependency found",
                        'details': vuln
                    })
        except Exception as e:
            self.logger.error(f"Failed to analyze dependencies: {e}")

    def generate_recommendations(self) -> None:
        """Generate security recommendations based on findings."""
        severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for issue in self.report_data['issues']:
            severity_count[issue['severity']] += 1
            
            if issue['type'] == 'file_permission':
                self.report_data['recommendations'].append(
                    f"Fix file permissions for {issue['details']}"
                )
            elif issue['type'] == 'network_security':
                self.report_data['recommendations'].append(
                    f"Close unauthorized port {issue['details']}"
                )
            elif issue['type'] == 'encryption':
                self.report_data['recommendations'].append(
                    f"Address encryption issue: {issue['description']}"
                )
            elif issue['type'] == 'access_control':
                self.report_data['recommendations'].append(
                    f"Fix access control configuration: {issue['description']}"
                )
            elif issue['type'] == 'security_headers':
                self.report_data['recommendations'].append(
                    f"Add missing security header: {issue['description']}"
                )
            elif issue['type'] == 'dependency':
                self.report_data['recommendations'].append(
                    f"Update vulnerable dependency: {issue['details']}"
                )
        
        self.report_data['summary'] = {
            'total_issues': len(self.report_data['issues']),
            'severity_breakdown': severity_count
        }

    def run_audit(self) -> None:
        """Run all security audit checks."""
        self.logger.info("Starting security audit...")
        
        audit_tasks = [
            self.check_file_permissions,
            self.audit_network_security,
            self.check_encryption_configuration,
            self.audit_access_control,
            self.check_security_headers,
            self.analyze_dependencies
        ]
        
        for task in audit_tasks:
            try:
                task()
            except Exception as e:
                self.logger.error(f"Error in {task.__name__}: {e}")
        
        self.generate_recommendations()
        
        # Generate report
        report_path = Path('security/reports')
        report_path.mkdir(parents=True, exist_ok=True)
        
        report_file = report_path / f"security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        self.logger.info(f"""
        Security audit completed:
        - Total issues: {self.report_data['summary']['total_issues']}
        - Critical: {self.report_data['summary']['severity_breakdown']['CRITICAL']}
        - High: {self.report_data['summary']['severity_breakdown']['HIGH']}
        - Medium: {self.report_data['summary']['severity_breakdown']['MEDIUM']}
        - Low: {self.report_data['summary']['severity_breakdown']['LOW']}
        
        Report saved to: {report_file}
        """)

def main():
    if len(sys.argv) != 2:
        print("Usage: python security_audit.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    auditor = SecurityAuditor(config_path)
    auditor.run_audit()

if __name__ == "__main__":
    main()
