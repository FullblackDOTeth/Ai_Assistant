"""
Verify Head AI server connection and status
"""

import sys
from pathlib import Path
import requests
import yaml
import socket
import psutil
import json
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from src.core.server_manager import server_manager

class ServerVerification:
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / 'config' / 'server_config.yaml'
        self.config = self._load_config()
        self.host = self.config['server']['host']
        self.port = self.config['server']['port']

    def _load_config(self):
        """Load server configuration"""
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def check_port_available(self):
        """Check if server port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((self.host, self.port))
            result = True
        except:
            result = False
        finally:
            sock.close()
        return result

    def check_server_process(self):
        """Check for running server process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('server' in cmd.lower() for cmd in cmdline):
                        return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def test_server_connection(self):
        """Test connection to server"""
        url = f"http://{self.host}:{self.port}/health"
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def check_ssl_configuration(self):
        """Verify SSL configuration"""
        ssl_config = self.config['security']['ssl']
        if not ssl_config['enabled']:
            return "SSL not enabled"
        
        cert_path = Path(ssl_config['cert_path'])
        key_path = Path(ssl_config['key_path'])
        
        return {
            'cert_exists': cert_path.exists(),
            'key_exists': key_path.exists()
        }

    def get_system_resources(self):
        """Get system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

    def run_verification(self):
        """Run all verification checks"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'admin_mode': server_manager.is_admin(),
            'port_available': self.check_port_available(),
            'server_process': self.check_server_process(),
            'server_connection': self.test_server_connection(),
            'ssl_status': self.check_ssl_configuration(),
            'system_resources': self.get_system_resources()
        }
        
        return results

def main():
    """Run server verification and display results"""
    print("Verifying Head AI Server...\n")
    
    verifier = ServerVerification()
    results = verifier.run_verification()
    
    print("Server Status:")
    print(f"✓ Admin Mode: {'Enabled' if results['admin_mode'] else 'Disabled'}")
    print(f"{'✓' if results['port_available'] else '✗'} Port {verifier.port}: "
          f"{'Available' if results['port_available'] else 'In Use'}")
    print(f"{'✓' if results['server_process'] else '✗'} Server Process: "
          f"{'Running (PID: ' + str(results['server_process']) + ')' if results['server_process'] else 'Not Found'}")
    print(f"{'✓' if results['server_connection'] else '✗'} Server Connection: "
          f"{'Connected' if results['server_connection'] else 'Failed'}")
    
    print("\nSSL Configuration:")
    if isinstance(results['ssl_status'], str):
        print(f"ℹ {results['ssl_status']}")
    else:
        print(f"{'✓' if results['ssl_status']['cert_exists'] else '✗'} SSL Certificate")
        print(f"{'✓' if results['ssl_status']['key_exists'] else '✗'} SSL Key")
    
    print("\nSystem Resources:")
    resources = results['system_resources']
    print(f"CPU Usage: {resources['cpu_percent']}%")
    print(f"Memory Usage: {resources['memory_percent']}%")
    print(f"Disk Usage: {resources['disk_usage']}%")
    
    # Save results
    output_file = Path(__file__).parent.parent / 'logs' / 'server_verification.json'
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Return success based on critical checks
    return (results['admin_mode'] and 
            (results['server_process'] is not None or results['port_available']) and
            resources['cpu_percent'] < 90 and
            resources['memory_percent'] < 90)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
