#!/usr/bin/env python3

import os
import json
import logging
import asyncio
import aiohttp
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Union
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import nmap
import shodan
from pymetasploit3.msfrpc import MsfRpcClient
import openvas_lib
from zapv2 import ZAPv2
import nuclei
from concurrent.futures import ThreadPoolExecutor

class SecurityTestingService:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.db_engine = self._setup_database()
        self._setup_tools()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for security testing service."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_testing.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('SecurityTestingService')

    def _load_config(self, config_path: str) -> Dict:
        """Load security testing configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _setup_database(self):
        """Set up database connection."""
        db_config = self.config['database']
        return create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['name']}"
        )

    def _setup_tools(self):
        """Initialize security testing tools."""
        try:
            # Initialize Nmap scanner
            self.nmap_scanner = nmap.PortScanner()
            
            # Initialize Shodan client
            self.shodan_client = shodan.Shodan(self.config['api_keys']['shodan'])
            
            # Initialize Metasploit RPC client
            self.msf_client = MsfRpcClient(
                self.config['metasploit']['password'],
                server=self.config['metasploit']['host'],
                port=self.config['metasploit']['port']
            )
            
            # Initialize OpenVAS client
            self.openvas_client = openvas_lib.VulnscanManager(
                self.config['openvas']['host'],
                self.config['openvas']['username'],
                self.config['openvas']['password'],
                self.config['openvas']['port']
            )
            
            # Initialize OWASP ZAP client
            self.zap = ZAPv2(
                proxies={'http': self.config['zap']['proxy_url']}
            )
            
            # Initialize Nuclei scanner
            self.nuclei_scanner = nuclei.Scanner()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security tools: {str(e)}")
            raise

    async def run_vulnerability_scan(self, target: str, scan_type: str = 'full') -> Dict:
        """Run comprehensive vulnerability scan."""
        try:
            scan_results = {
                'timestamp': datetime.now().isoformat(),
                'target': target,
                'scan_type': scan_type,
                'vulnerabilities': [],
                'summary': {}
            }
            
            # Run parallel scans
            async with asyncio.TaskGroup() as tg:
                nmap_task = tg.create_task(self._run_nmap_scan(target))
                openvas_task = tg.create_task(self._run_openvas_scan(target))
                zap_task = tg.create_task(self._run_zap_scan(target))
                nuclei_task = tg.create_task(self._run_nuclei_scan(target))
            
            # Collect results
            scan_results['vulnerabilities'].extend(nmap_task.result())
            scan_results['vulnerabilities'].extend(openvas_task.result())
            scan_results['vulnerabilities'].extend(zap_task.result())
            scan_results['vulnerabilities'].extend(nuclei_task.result())
            
            # Generate summary
            scan_results['summary'] = self._generate_vulnerability_summary(
                scan_results['vulnerabilities']
            )
            
            # Store results
            self._store_scan_results(scan_results)
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"Vulnerability scan failed: {str(e)}")
            raise

    async def run_penetration_test(self, target: str, test_type: str = 'full') -> Dict:
        """Run automated penetration test."""
        try:
            test_results = {
                'timestamp': datetime.now().isoformat(),
                'target': target,
                'test_type': test_type,
                'findings': [],
                'summary': {}
            }
            
            # Run parallel tests
            async with asyncio.TaskGroup() as tg:
                msf_task = tg.create_task(self._run_metasploit_test(target))
                custom_task = tg.create_task(self._run_custom_exploits(target))
            
            # Collect results
            test_results['findings'].extend(msf_task.result())
            test_results['findings'].extend(custom_task.result())
            
            # Generate summary
            test_results['summary'] = self._generate_pentest_summary(
                test_results['findings']
            )
            
            # Store results
            self._store_pentest_results(test_results)
            
            return test_results
            
        except Exception as e:
            self.logger.error(f"Penetration test failed: {str(e)}")
            raise

    async def _run_nmap_scan(self, target: str) -> List[Dict]:
        """Run Nmap vulnerability scan."""
        try:
            vulnerabilities = []
            
            # Run Nmap scan with NSE scripts
            self.nmap_scanner.scan(
                target,
                arguments='-sV -sC --script vuln'
            )
            
            # Parse results
            for host in self.nmap_scanner.all_hosts():
                host_vulns = self.nmap_scanner[host]
                for port in host_vulns.all_tcp():
                    if 'script' in host_vulns['tcp'][port]:
                        for script, output in host_vulns['tcp'][port]['script'].items():
                            vulnerabilities.append({
                                'type': 'nmap',
                                'host': host,
                                'port': port,
                                'service': host_vulns['tcp'][port].get('name', ''),
                                'vulnerability': script,
                                'details': output
                            })
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"Nmap scan failed: {str(e)}")
            return []

    async def _run_openvas_scan(self, target: str) -> List[Dict]:
        """Run OpenVAS vulnerability scan."""
        try:
            vulnerabilities = []
            
            # Start scan
            scan_id, target_id = self.openvas_client.launch_scan(
                target_name=f"Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                target=target,
                profile="Full and fast"
            )
            
            # Wait for scan completion
            while self.openvas_client.get_scan_status(scan_id) != 'Done':
                await asyncio.sleep(30)
            
            # Get results
            report_id = self.openvas_client.get_report_id(scan_id)
            report = self.openvas_client.get_report_xml(report_id)
            
            # Parse results
            for result in report.findall('.//result'):
                vulnerabilities.append({
                    'type': 'openvas',
                    'host': result.find('host').text,
                    'name': result.find('name').text,
                    'severity': result.find('severity').text,
                    'description': result.find('description').text,
                    'solution': result.find('solution').text if result.find('solution') is not None else ''
                })
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"OpenVAS scan failed: {str(e)}")
            return []

    async def _run_zap_scan(self, target: str) -> List[Dict]:
        """Run OWASP ZAP vulnerability scan."""
        try:
            vulnerabilities = []
            
            # Start ZAP spider
            scan_id = self.zap.spider.scan(target)
            
            # Wait for spider completion
            while int(self.zap.spider.status(scan_id)) < 100:
                await asyncio.sleep(5)
            
            # Start active scan
            scan_id = self.zap.ascan.scan(target)
            
            # Wait for scan completion
            while int(self.zap.ascan.status(scan_id)) < 100:
                await asyncio.sleep(5)
            
            # Get results
            for alert in self.zap.core.alerts():
                vulnerabilities.append({
                    'type': 'zap',
                    'risk': alert['risk'],
                    'url': alert['url'],
                    'name': alert['name'],
                    'description': alert['description'],
                    'solution': alert['solution'],
                    'evidence': alert['evidence']
                })
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"ZAP scan failed: {str(e)}")
            return []

    async def _run_nuclei_scan(self, target: str) -> List[Dict]:
        """Run Nuclei vulnerability scan."""
        try:
            vulnerabilities = []
            
            # Run Nuclei scan
            results = self.nuclei_scanner.scan(
                target,
                templates=['cves', 'vulnerabilities', 'misconfiguration']
            )
            
            # Parse results
            for result in results:
                vulnerabilities.append({
                    'type': 'nuclei',
                    'template': result.template_id,
                    'severity': result.severity,
                    'host': result.host,
                    'matched': result.matched,
                    'description': result.info.description,
                    'reference': result.info.reference
                })
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"Nuclei scan failed: {str(e)}")
            return []

    async def _run_metasploit_test(self, target: str) -> List[Dict]:
        """Run Metasploit penetration test."""
        try:
            findings = []
            
            # Get workspace
            workspace = self.msf_client.pro.workspaces().workspaces[0]
            
            # Import vulnerabilities
            self.msf_client.pro.import_data(
                workspace['name'],
                self.config['metasploit']['import_file']
            )
            
            # Run exploitation
            task = self.msf_client.pro.start_exploit(
                workspace['name'],
                target,
                self.config['metasploit']['exploit_timeout']
            )
            
            # Wait for completion
            while task['status'] != 'completed':
                await asyncio.sleep(30)
                task = self.msf_client.pro.task_status(task['task_id'])
            
            # Get results
            for session in self.msf_client.sessions.list:
                findings.append({
                    'type': 'metasploit',
                    'session_id': session.id,
                    'type': session.type,
                    'exploit': session.via_exploit,
                    'payload': session.via_payload,
                    'info': session.info,
                    'platform': session.platform
                })
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Metasploit test failed: {str(e)}")
            return []

    async def _run_custom_exploits(self, target: str) -> List[Dict]:
        """Run custom exploitation techniques."""
        try:
            findings = []
            
            # Load custom exploits
            with open(self.config['custom_exploits']['path'], 'r') as f:
                exploits = json.load(f)
            
            # Run each exploit
            for exploit in exploits:
                result = await self._run_single_exploit(target, exploit)
                if result:
                    findings.append(result)
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Custom exploitation failed: {str(e)}")
            return []

    def _generate_vulnerability_summary(self, vulnerabilities: List[Dict]) -> Dict:
        """Generate summary of vulnerability scan results."""
        summary = {
            'total_vulnerabilities': len(vulnerabilities),
            'severity_counts': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            },
            'tool_counts': {},
            'top_vulnerabilities': []
        }
        
        # Count vulnerabilities by severity and tool
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info').lower()
            tool = vuln.get('type', 'unknown')
            
            summary['severity_counts'][severity] += 1
            summary['tool_counts'][tool] = summary['tool_counts'].get(tool, 0) + 1
        
        # Get top vulnerabilities
        summary['top_vulnerabilities'] = sorted(
            vulnerabilities,
            key=lambda x: x.get('severity', 'info'),
            reverse=True
        )[:10]
        
        return summary

    def _generate_pentest_summary(self, findings: List[Dict]) -> Dict:
        """Generate summary of penetration test results."""
        summary = {
            'total_findings': len(findings),
            'successful_exploits': 0,
            'tool_counts': {},
            'top_findings': []
        }
        
        # Count findings by type and success
        for finding in findings:
            tool = finding.get('type', 'unknown')
            summary['tool_counts'][tool] = summary['tool_counts'].get(tool, 0) + 1
            
            if finding.get('session_id'):
                summary['successful_exploits'] += 1
        
        # Get top findings
        summary['top_findings'] = sorted(
            findings,
            key=lambda x: bool(x.get('session_id')),
            reverse=True
        )[:10]
        
        return summary

    def _store_scan_results(self, results: Dict):
        """Store vulnerability scan results in database."""
        try:
            Session = sessionmaker(bind=self.db_engine)
            session = Session()
            
            # Store results (implement database schema and models)
            
            session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store scan results: {str(e)}")
            raise
        finally:
            session.close()

    def _store_pentest_results(self, results: Dict):
        """Store penetration test results in database."""
        try:
            Session = sessionmaker(bind=self.db_engine)
            session = Session()
            
            # Store results (implement database schema and models)
            
            session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store pentest results: {str(e)}")
            raise
        finally:
            session.close()

def main():
    """Main entry point for security testing service."""
    try:
        service = SecurityTestingService('config/security.json')
        
        # Run security tests
        asyncio.run(service.run_vulnerability_scan('target_host'))
        asyncio.run(service.run_penetration_test('target_host'))
        
        print("Security testing completed successfully")
        
    except Exception as e:
        print(f"Security testing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
