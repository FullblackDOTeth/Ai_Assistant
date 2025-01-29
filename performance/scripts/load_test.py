#!/usr/bin/env python3

import os
import sys
import json
import logging
import asyncio
import aiohttp
import numpy as np
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'endpoints': {},
            'errors': [],
            'recommendations': []
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('load_testing.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('LoadTester')

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return json.load(f)

    async def _make_request(self, session: aiohttp.ClientSession, 
                          endpoint: str, method: str, 
                          payload: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a single HTTP request and measure performance."""
        start_time = time.time()
        
        try:
            async with session.request(method, endpoint, json=payload) as response:
                await response.read()
                end_time = time.time()
                
                return {
                    'status': response.status,
                    'time': end_time - start_time,
                    'success': 200 <= response.status < 300
                }
                
        except Exception as e:
            end_time = time.time()
            self.results['errors'].append({
                'endpoint': endpoint,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return {
                'status': 0,
                'time': end_time - start_time,
                'success': False
            }

    async def run_load_test(self, endpoint: str, method: str, 
                           users: int, duration: int,
                           payload: Optional[Dict] = None) -> None:
        """Run a load test for a specific endpoint."""
        self.logger.info(f"Starting load test for {endpoint} with {users} users for {duration}s")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []
            request_times = []
            
            while time.time() - start_time < duration:
                if len(tasks) < users:
                    # Add new tasks up to the user limit
                    while len(tasks) < users:
                        task = asyncio.create_task(
                            self._make_request(session, endpoint, method, payload)
                        )
                        tasks.append(task)
                
                # Wait for any task to complete
                done, tasks = await asyncio.wait(
                    tasks, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed requests
                for task in done:
                    result = await task
                    if result['success']:
                        request_times.append(result['time'])
            
            # Wait for remaining tasks
            if tasks:
                done, _ = await asyncio.wait(tasks)
                for task in done:
                    result = await task
                    if result['success']:
                        request_times.append(result['time'])
            
            # Calculate statistics
            if request_times:
                times = np.array(request_times)
                self.results['endpoints'][endpoint] = {
                    'min_time': float(np.min(times)),
                    'max_time': float(np.max(times)),
                    'mean_time': float(np.mean(times)),
                    'median_time': float(np.median(times)),
                    'p95_time': float(np.percentile(times, 95)),
                    'p99_time': float(np.percentile(times, 99)),
                    'std_dev': float(np.std(times)),
                    'total_requests': len(request_times),
                    'requests_per_second': len(request_times) / duration
                }
                
                # Generate recommendations based on results
                stats = self.results['endpoints'][endpoint]
                if stats['p95_time'] > 1.0:  # Response time > 1s for 95th percentile
                    self.results['recommendations'].append({
                        'type': 'response_time',
                        'severity': 'high',
                        'endpoint': endpoint,
                        'message': f'Slow response time (P95: {stats["p95_time"]:.2f}s). Consider optimization.'
                    })
                
                if stats['std_dev'] > stats['mean_time']:  # High variance
                    self.results['recommendations'].append({
                        'type': 'variance',
                        'severity': 'medium',
                        'endpoint': endpoint,
                        'message': f'High response time variance. Consider investigating inconsistent performance.'
                    })

    async def run_stress_test(self, endpoint: str, method: str,
                            start_users: int, max_users: int,
                            step_users: int, step_duration: int,
                            payload: Optional[Dict] = None) -> None:
        """Run a stress test with increasing user load."""
        self.logger.info(f"Starting stress test for {endpoint}")
        
        stress_results = []
        current_users = start_users
        
        while current_users <= max_users:
            self.logger.info(f"Testing with {current_users} users")
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                request_times = []
                start_time = time.time()
                
                while time.time() - start_time < step_duration:
                    while len(tasks) < current_users:
                        task = asyncio.create_task(
                            self._make_request(session, endpoint, method, payload)
                        )
                        tasks.append(task)
                    
                    done, tasks = await asyncio.wait(
                        tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in done:
                        result = await task
                        if result['success']:
                            request_times.append(result['time'])
                
                # Wait for remaining tasks
                if tasks:
                    done, _ = await asyncio.wait(tasks)
                    for task in done:
                        result = await task
                        if result['success']:
                            request_times.append(result['time'])
                
                # Calculate statistics for this step
                if request_times:
                    times = np.array(request_times)
                    stress_results.append({
                        'users': current_users,
                        'min_time': float(np.min(times)),
                        'max_time': float(np.max(times)),
                        'mean_time': float(np.mean(times)),
                        'p95_time': float(np.percentile(times, 95)),
                        'requests_per_second': len(request_times) / step_duration
                    })
                
                # Check for breaking point
                if stress_results[-1]['p95_time'] > 2.0:  # P95 > 2s
                    self.results['recommendations'].append({
                        'type': 'capacity',
                        'severity': 'high',
                        'endpoint': endpoint,
                        'message': f'System capacity reached at {current_users} users.'
                    })
                    break
            
            current_users += step_users
        
        self.results['stress_test'] = {
            'endpoint': endpoint,
            'steps': stress_results
        }

    async def run_spike_test(self, endpoint: str, method: str,
                            base_users: int, spike_users: int,
                            duration: int, payload: Optional[Dict] = None) -> None:
        """Run a spike test with sudden increase in users."""
        self.logger.info(f"Starting spike test for {endpoint}")
        
        async with aiohttp.ClientSession() as session:
            # Baseline period
            baseline_tasks = []
            baseline_times = []
            
            # Run baseline load
            start_time = time.time()
            while time.time() - start_time < duration / 3:  # First third is baseline
                while len(baseline_tasks) < base_users:
                    task = asyncio.create_task(
                        self._make_request(session, endpoint, method, payload)
                    )
                    baseline_tasks.append(task)
                
                done, baseline_tasks = await asyncio.wait(
                    baseline_tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    result = await task
                    if result['success']:
                        baseline_times.append(result['time'])
            
            # Spike period
            spike_tasks = []
            spike_times = []
            
            # Run spike load
            start_time = time.time()
            while time.time() - start_time < duration / 3:  # Second third is spike
                while len(spike_tasks) < spike_users:
                    task = asyncio.create_task(
                        self._make_request(session, endpoint, method, payload)
                    )
                    spike_tasks.append(task)
                
                done, spike_tasks = await asyncio.wait(
                    spike_tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    result = await task
                    if result['success']:
                        spike_times.append(result['time'])
            
            # Recovery period
            recovery_tasks = []
            recovery_times = []
            
            # Run recovery period
            start_time = time.time()
            while time.time() - start_time < duration / 3:  # Last third is recovery
                while len(recovery_tasks) < base_users:
                    task = asyncio.create_task(
                        self._make_request(session, endpoint, method, payload)
                    )
                    recovery_tasks.append(task)
                
                done, recovery_tasks = await asyncio.wait(
                    recovery_tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    result = await task
                    if result['success']:
                        recovery_times.append(result['time'])
            
            # Calculate statistics for each period
            self.results['spike_test'] = {
                'endpoint': endpoint,
                'baseline': {
                    'users': base_users,
                    'mean_time': float(np.mean(baseline_times)),
                    'p95_time': float(np.percentile(baseline_times, 95))
                },
                'spike': {
                    'users': spike_users,
                    'mean_time': float(np.mean(spike_times)),
                    'p95_time': float(np.percentile(spike_times, 95))
                },
                'recovery': {
                    'users': base_users,
                    'mean_time': float(np.mean(recovery_times)),
                    'p95_time': float(np.percentile(recovery_times, 95))
                }
            }
            
            # Analyze recovery
            baseline_mean = np.mean(baseline_times)
            recovery_mean = np.mean(recovery_times)
            
            if recovery_mean > baseline_mean * 1.2:  # Recovery time >20% higher than baseline
                self.results['recommendations'].append({
                    'type': 'recovery',
                    'severity': 'high',
                    'endpoint': endpoint,
                    'message': f'Slow recovery after spike (Baseline: {baseline_mean:.2f}s, Recovery: {recovery_mean:.2f}s)'
                })

    def generate_report(self) -> None:
        """Generate a detailed load testing report."""
        try:
            report_dir = Path('performance/reports')
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / f"load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Calculate overall statistics
            total_requests = sum(
                endpoint['total_requests']
                for endpoint in self.results['endpoints'].values()
            )
            
            total_errors = len(self.results['errors'])
            
            self.results['summary'] = {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate': total_errors / total_requests if total_requests > 0 else 0,
                'test_duration': time.time() - self.results['timestamp']
            }
            
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            self.logger.info(f"""
            Load testing completed:
            - Total Requests: {total_requests}
            - Total Errors: {total_errors}
            - Error Rate: {self.results['summary']['error_rate']:.2%}
            - Recommendations: {len(self.results['recommendations'])}
            
            Report saved to: {report_file}
            """)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

async def main():
    if len(sys.argv) != 2:
        print("Usage: python load_test.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    tester = LoadTester(config_path)
    
    # Example test scenarios
    await tester.run_load_test(
        endpoint="http://api.example.com/endpoint",
        method="GET",
        users=100,
        duration=300
    )
    
    await tester.run_stress_test(
        endpoint="http://api.example.com/endpoint",
        method="GET",
        start_users=10,
        max_users=200,
        step_users=10,
        step_duration=60
    )
    
    await tester.run_spike_test(
        endpoint="http://api.example.com/endpoint",
        method="GET",
        base_users=50,
        spike_users=500,
        duration=300
    )
    
    tester.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
