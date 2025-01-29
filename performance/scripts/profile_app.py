#!/usr/bin/env python3

import cProfile
import pstats
import io
import time
import sys
import os
import psutil
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import numpy as np
from memory_profiler import profile as memory_profile

class PerformanceProfiler:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'cpu_profiling': {},
            'memory_profiling': {},
            'io_profiling': {},
            'network_profiling': {},
            'database_profiling': {},
            'recommendations': []
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('performance_profiling.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('PerformanceProfiler')

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return json.load(f)

    def profile_cpu(self, target_function: callable, *args, **kwargs) -> None:
        """Profile CPU usage of a target function."""
        self.logger.info("Starting CPU profiling...")
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = target_function(*args, **kwargs)
            profiler.disable()
            
            s = io.StringIO()
            stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            stats.print_stats()
            
            self.results['cpu_profiling'] = {
                'stats': s.getvalue(),
                'total_time': stats.total_tt,
                'function_calls': stats.total_calls
            }
            
            # Analyze hotspots
            hotspots = []
            for func, (cc, nc, tt, ct, callers) in stats.stats.items():
                if ct > stats.total_tt * 0.1:  # Functions taking >10% of total time
                    hotspots.append({
                        'function': f"{func[2]}:{func[1]}",
                        'calls': cc,
                        'time': ct,
                        'percentage': (ct / stats.total_tt) * 100
                    })
            
            self.results['cpu_profiling']['hotspots'] = hotspots
            
        except Exception as e:
            self.logger.error(f"CPU profiling failed: {e}")
            raise

    @memory_profile
    def profile_memory(self, target_function: callable, *args, **kwargs) -> None:
        """Profile memory usage of a target function."""
        self.logger.info("Starting memory profiling...")
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            start_time = time.time()
            result = target_function(*args, **kwargs)
            end_time = time.time()
            
            final_memory = process.memory_info().rss
            memory_diff = final_memory - initial_memory
            
            self.results['memory_profiling'] = {
                'initial_memory_mb': initial_memory / (1024 * 1024),
                'final_memory_mb': final_memory / (1024 * 1024),
                'memory_increase_mb': memory_diff / (1024 * 1024),
                'execution_time': end_time - start_time
            }
            
            # Check for memory leaks
            if memory_diff > 100 * 1024 * 1024:  # 100MB threshold
                self.results['recommendations'].append({
                    'type': 'memory',
                    'severity': 'high',
                    'message': f'Potential memory leak detected: {memory_diff / (1024 * 1024):.2f}MB increase'
                })
                
        except Exception as e:
            self.logger.error(f"Memory profiling failed: {e}")
            raise

    async def profile_io(self, target_function: callable, *args, **kwargs) -> None:
        """Profile I/O operations of a target function."""
        self.logger.info("Starting I/O profiling...")
        
        try:
            process = psutil.Process()
            initial_io = process.io_counters()
            
            start_time = time.time()
            result = await target_function(*args, **kwargs)
            end_time = time.time()
            
            final_io = process.io_counters()
            
            self.results['io_profiling'] = {
                'read_bytes': final_io.read_bytes - initial_io.read_bytes,
                'write_bytes': final_io.write_bytes - initial_io.write_bytes,
                'read_count': final_io.read_count - initial_io.read_count,
                'write_count': final_io.write_count - initial_io.write_count,
                'execution_time': end_time - start_time
            }
            
            # Analyze I/O patterns
            bytes_per_second = (final_io.read_bytes + final_io.write_bytes) / (end_time - start_time)
            if bytes_per_second > 10 * 1024 * 1024:  # 10MB/s threshold
                self.results['recommendations'].append({
                    'type': 'io',
                    'severity': 'medium',
                    'message': f'High I/O usage detected: {bytes_per_second / (1024 * 1024):.2f}MB/s'
                })
                
        except Exception as e:
            self.logger.error(f"I/O profiling failed: {e}")
            raise

    async def profile_network(self, target_function: callable, *args, **kwargs) -> None:
        """Profile network operations of a target function."""
        self.logger.info("Starting network profiling...")
        
        try:
            initial_net = psutil.net_io_counters()
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                result = await target_function(session, *args, **kwargs)
                end_time = time.time()
            
            final_net = psutil.net_io_counters()
            
            self.results['network_profiling'] = {
                'bytes_sent': final_net.bytes_sent - initial_net.bytes_sent,
                'bytes_recv': final_net.bytes_recv - initial_net.bytes_recv,
                'packets_sent': final_net.packets_sent - initial_net.packets_sent,
                'packets_recv': final_net.packets_recv - initial_net.packets_recv,
                'execution_time': end_time - start_time
            }
            
            # Analyze network patterns
            bandwidth = (final_net.bytes_sent + final_net.bytes_recv) / (end_time - start_time)
            if bandwidth > 5 * 1024 * 1024:  # 5MB/s threshold
                self.results['recommendations'].append({
                    'type': 'network',
                    'severity': 'medium',
                    'message': f'High network usage detected: {bandwidth / (1024 * 1024):.2f}MB/s'
                })
                
        except Exception as e:
            self.logger.error(f"Network profiling failed: {e}")
            raise

    def analyze_results(self) -> None:
        """Analyze profiling results and generate recommendations."""
        try:
            # CPU Analysis
            if 'cpu_profiling' in self.results:
                cpu_time = self.results['cpu_profiling'].get('total_time', 0)
                if cpu_time > 1.0:  # More than 1 second
                    self.results['recommendations'].append({
                        'type': 'cpu',
                        'severity': 'medium',
                        'message': f'High CPU time detected: {cpu_time:.2f}s. Consider optimizing hotspots.'
                    })

            # Memory Analysis
            if 'memory_profiling' in self.results:
                memory_increase = self.results['memory_profiling'].get('memory_increase_mb', 0)
                if memory_increase > 100:  # More than 100MB
                    self.results['recommendations'].append({
                        'type': 'memory',
                        'severity': 'high',
                        'message': f'High memory usage increase: {memory_increase:.2f}MB. Check for memory leaks.'
                    })

            # I/O Analysis
            if 'io_profiling' in self.results:
                io_ops = self.results['io_profiling'].get('read_count', 0) + \
                        self.results['io_profiling'].get('write_count', 0)
                if io_ops > 1000:  # More than 1000 I/O operations
                    self.results['recommendations'].append({
                        'type': 'io',
                        'severity': 'medium',
                        'message': f'High I/O operations count: {io_ops}. Consider caching or buffering.'
                    })

            # Network Analysis
            if 'network_profiling' in self.results:
                network_bytes = self.results['network_profiling'].get('bytes_sent', 0) + \
                              self.results['network_profiling'].get('bytes_recv', 0)
                if network_bytes > 10 * 1024 * 1024:  # More than 10MB
                    self.results['recommendations'].append({
                        'type': 'network',
                        'severity': 'medium',
                        'message': f'High network usage: {network_bytes / (1024 * 1024):.2f}MB. Consider data compression.'
                    })

        except Exception as e:
            self.logger.error(f"Results analysis failed: {e}")
            raise

    def generate_report(self) -> None:
        """Generate a detailed performance report."""
        try:
            report_dir = Path('performance/reports')
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            self.logger.info(f"""
            Performance profiling completed:
            - CPU Profiling: {len(self.results.get('cpu_profiling', {}).get('hotspots', [])) } hotspots identified
            - Memory Profiling: {self.results.get('memory_profiling', {}).get('memory_increase_mb', 0):.2f}MB increase
            - I/O Profiling: {self.results.get('io_profiling', {}).get('read_count', 0)} read ops, {self.results.get('io_profiling', {}).get('write_count', 0)} write ops
            - Network Profiling: {self.results.get('network_profiling', {}).get('bytes_sent', 0) / (1024 * 1024):.2f}MB sent, {self.results.get('network_profiling', {}).get('bytes_recv', 0) / (1024 * 1024):.2f}MB received
            - Recommendations: {len(self.results['recommendations'])} items
            
            Report saved to: {report_file}
            """)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

async def main():
    if len(sys.argv) != 2:
        print("Usage: python profile_app.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    profiler = PerformanceProfiler(config_path)
    
    # Example target functions for profiling
    def cpu_intensive_task():
        return sum(i * i for i in range(1000000))
    
    def memory_intensive_task():
        return [i * i for i in range(1000000)]
    
    async def io_intensive_task():
        with open('large_file.txt', 'w') as f:
            f.write('x' * 1000000)
        with open('large_file.txt', 'r') as f:
            content = f.read()
        os.remove('large_file.txt')
        return len(content)
    
    async def network_intensive_task(session):
        async with session.get('https://api.example.com/data') as response:
            return await response.json()
    
    try:
        # Run profiling tasks
        profiler.profile_cpu(cpu_intensive_task)
        profiler.profile_memory(memory_intensive_task)
        await profiler.profile_io(io_intensive_task)
        await profiler.profile_network(network_intensive_task)
        
        # Analyze results and generate report
        profiler.analyze_results()
        profiler.generate_report()
        
    except Exception as e:
        profiler.logger.error(f"Profiling failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
