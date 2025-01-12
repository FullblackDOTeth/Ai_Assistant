#!/usr/bin/env python3

import os
import json
import logging
import time
import cProfile
import pstats
import memory_profiler
import psutil
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import aiohttp
import locust
from locust import HttpUser, task, between
import line_profiler
import objgraph
import py-spy
from guppy3 import hpy
import redis
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

class PerformanceTestingService:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.db_engine = self._setup_database()
        self.redis_client = self._setup_redis()
        self.metrics_registry = CollectorRegistry()
        self._setup_metrics()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for performance testing service."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('performance_testing.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('PerformanceTestingService')

    def _load_config(self, config_path: str) -> Dict:
        """Load performance testing configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _setup_database(self):
        """Set up database connection."""
        db_config = self.config['database']
        return create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['name']}"
        )

    def _setup_redis(self):
        """Set up Redis connection."""
        redis_config = self.config['redis']
        return redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            password=redis_config['password'],
            db=redis_config.get('db', 0)
        )

    def _setup_metrics(self):
        """Set up Prometheus metrics."""
        self.metrics = {
            'response_time': Histogram(
                'response_time_seconds',
                'Response time in seconds',
                ['endpoint'],
                registry=self.metrics_registry
            ),
            'memory_usage': Gauge(
                'memory_usage_bytes',
                'Memory usage in bytes',
                ['type'],
                registry=self.metrics_registry
            ),
            'cpu_usage': Gauge(
                'cpu_usage_percent',
                'CPU usage percentage',
                registry=self.metrics_registry
            ),
            'database_queries': Counter(
                'database_queries_total',
                'Total database queries',
                ['type'],
                registry=self.metrics_registry
            )
        }

    async def run_code_profiling(self, target_module: str) -> Dict:
        """Profile code execution and memory usage."""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'target': target_module,
                'cpu_profile': {},
                'memory_profile': {},
                'line_profile': {},
                'object_graph': {}
            }
            
            # CPU profiling
            profiler = cProfile.Profile()
            profiler.enable()
            
            # Import and run target module
            module = __import__(target_module)
            module.main()
            
            profiler.disable()
            stats = pstats.Stats(profiler)
            
            # Get top functions by cumulative time
            results['cpu_profile']['top_functions'] = stats.get_stats_profile().func_profiles
            
            # Memory profiling
            mem_usage = memory_profiler.profile(module.main)()
            results['memory_profile']['memory_usage'] = mem_usage
            
            # Line profiling
            line_prof = line_profiler.LineProfiler()
            line_prof.add_function(module.main)
            line_prof.run('module.main()')
            results['line_profile'] = line_prof.get_stats()
            
            # Object graph analysis
            objgraph.show_most_common_types(limit=20)
            results['object_graph'] = objgraph.get_leaking_objects()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Code profiling failed: {str(e)}")
            raise

    async def optimize_database_queries(self, target_queries: List[str]) -> Dict:
        """Analyze and optimize database queries."""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'queries': [],
                'optimizations': []
            }
            
            for query in target_queries:
                # Analyze query execution plan
                explain_query = f"EXPLAIN ANALYZE {query}"
                with self.db_engine.connect() as conn:
                    plan = conn.execute(text(explain_query)).fetchall()
                
                # Parse execution plan
                analysis = self._analyze_query_plan(plan)
                
                # Generate optimization suggestions
                optimizations = self._generate_query_optimizations(analysis)
                
                results['queries'].append({
                    'query': query,
                    'execution_plan': plan,
                    'analysis': analysis,
                    'optimizations': optimizations
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Query optimization failed: {str(e)}")
            raise

    async def run_load_testing(self, target_url: str, config: Dict) -> Dict:
        """Run load testing using Locust."""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'target': target_url,
                'config': config,
                'metrics': {}
            }
            
            class WebsiteUser(HttpUser):
                wait_time = between(1, 2.5)
                
                @task(1)
                def test_endpoint(self):
                    self.client.get('/')
            
            # Run Locust test
            runner = locust.Runner([WebsiteUser], config)
            runner.start(config['num_users'], spawn_rate=config['spawn_rate'])
            
            # Collect metrics during test
            while runner.state == locust.STATE_RUNNING:
                await asyncio.sleep(1)
                results['metrics'] = runner.stats.serialize_stats()
            
            runner.stop()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Load testing failed: {str(e)}")
            raise

    async def analyze_memory_usage(self, target_process: str) -> Dict:
        """Analyze memory usage patterns."""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'process': target_process,
                'memory_analysis': {}
            }
            
            # Get process memory info
            process = psutil.Process()
            mem_info = process.memory_info()
            
            # Heap analysis
            h = hpy()
            heap = h.heap()
            
            results['memory_analysis'] = {
                'rss': mem_info.rss,
                'vms': mem_info.vms,
                'shared': mem_info.shared,
                'text': mem_info.text,
                'lib': mem_info.lib,
                'data': mem_info.data,
                'dirty': mem_info.dirty,
                'heap_by_type': heap.byrcs,
                'heap_by_size': heap.bysize
            }
            
            # Memory profiling
            snapshot = memory_profiler.take_snapshot()
            results['memory_analysis']['profile'] = snapshot.statistics('traceback')
            
            return results
            
        except Exception as e:
            self.logger.error(f"Memory analysis failed: {str(e)}")
            raise

    async def optimize_caching(self, target_functions: List[str]) -> Dict:
        """Analyze and optimize caching strategies."""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'functions': [],
                'recommendations': []
            }
            
            for func_name in target_functions:
                # Analyze function calls and data access patterns
                access_patterns = self._analyze_access_patterns(func_name)
                
                # Generate caching recommendations
                recommendations = self._generate_cache_recommendations(
                    func_name,
                    access_patterns
                )
                
                results['functions'].append({
                    'name': func_name,
                    'access_patterns': access_patterns,
                    'recommendations': recommendations
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Cache optimization failed: {str(e)}")
            raise

    def _analyze_query_plan(self, plan: List) -> Dict:
        """Analyze database query execution plan."""
        analysis = {
            'sequential_scans': 0,
            'index_scans': 0,
            'execution_time': 0,
            'bottlenecks': []
        }
        
        for step in plan:
            if 'Seq Scan' in step[0]:
                analysis['sequential_scans'] += 1
                analysis['bottlenecks'].append({
                    'type': 'sequential_scan',
                    'table': step[0].split('on ')[1],
                    'cost': float(step[0].split('cost=')[1].split('..')[1].split(' ')[0])
                })
            elif 'Index Scan' in step[0]:
                analysis['index_scans'] += 1
            
            if 'Execution Time' in step[0]:
                analysis['execution_time'] = float(step[0].split(': ')[1].split(' ms')[0])
        
        return analysis

    def _generate_query_optimizations(self, analysis: Dict) -> List[Dict]:
        """Generate query optimization recommendations."""
        optimizations = []
        
        # Check for excessive sequential scans
        if analysis['sequential_scans'] > 0:
            for bottleneck in analysis['bottlenecks']:
                if bottleneck['type'] == 'sequential_scan':
                    optimizations.append({
                        'type': 'create_index',
                        'table': bottleneck['table'],
                        'reason': 'High-cost sequential scan detected',
                        'suggestion': f"Create an index on the commonly filtered columns of {bottleneck['table']}"
                    })
        
        # Check execution time
        if analysis['execution_time'] > 1000:  # More than 1 second
            optimizations.append({
                'type': 'query_optimization',
                'reason': 'High execution time',
                'suggestion': 'Consider denormalization or materialized views'
            })
        
        return optimizations

    def _analyze_access_patterns(self, func_name: str) -> Dict:
        """Analyze function data access patterns."""
        patterns = {
            'read_frequency': {},
            'write_frequency': {},
            'data_lifetime': {},
            'data_size': {}
        }
        
        # Analyze Redis access patterns
        keys = self.redis_client.keys(f"{func_name}:*")
        for key in keys:
            ttl = self.redis_client.ttl(key)
            size = self.redis_client.memory_usage(key)
            
            patterns['data_lifetime'][key] = ttl
            patterns['data_size'][key] = size
        
        return patterns

    def _generate_cache_recommendations(self, func_name: str, patterns: Dict) -> List[Dict]:
        """Generate caching optimization recommendations."""
        recommendations = []
        
        # Analyze data lifetime
        for key, ttl in patterns['data_lifetime'].items():
            if ttl < 60:  # Less than 1 minute
                recommendations.append({
                    'type': 'increase_ttl',
                    'key': key,
                    'current_ttl': ttl,
                    'suggested_ttl': 300,
                    'reason': 'Short cache lifetime may cause unnecessary recomputation'
                })
        
        # Analyze data size
        for key, size in patterns['data_size'].items():
            if size > 1024 * 1024:  # More than 1MB
                recommendations.append({
                    'type': 'compress_data',
                    'key': key,
                    'current_size': size,
                    'reason': 'Large cache entries may impact memory usage'
                })
        
        return recommendations

def main():
    """Main entry point for performance testing service."""
    try:
        service = PerformanceTestingService('config/performance.json')
        
        # Run performance tests
        asyncio.run(service.run_code_profiling('target_module'))
        asyncio.run(service.optimize_database_queries(['SELECT * FROM users']))
        
        print("Performance testing completed successfully")
        
    except Exception as e:
        print(f"Performance testing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
