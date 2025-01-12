#!/usr/bin/env python3

import os
import sys
import json
import logging
import psycopg2
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

class DatabaseOptimizer:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.conn = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'table_stats': {},
            'index_stats': {},
            'query_stats': {},
            'recommendations': []
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('database_optimization.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('DatabaseOptimizer')

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return json.load(f)

    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                host=self.config['database']['host'],
                port=self.config['database']['port']
            )
            self.logger.info("Database connection established")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise

    def analyze_table_stats(self) -> None:
        """Analyze table statistics."""
        try:
            with self.conn.cursor() as cur:
                # Get table sizes and row counts
                cur.execute("""
                    SELECT
                        schemaname,
                        relname,
                        n_live_tup,
                        n_dead_tup,
                        pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                        pg_size_pretty(pg_table_size(relid)) as table_size,
                        pg_size_pretty(pg_indexes_size(relid)) as index_size
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(relid) DESC;
                """)
                
                for row in cur.fetchall():
                    schema, table, live_rows, dead_rows, total_size, table_size, index_size = row
                    self.results['table_stats'][f"{schema}.{table}"] = {
                        'live_rows': live_rows,
                        'dead_rows': dead_rows,
                        'total_size': total_size,
                        'table_size': table_size,
                        'index_size': index_size
                    }
                    
                    # Check for bloat
                    if dead_rows and (dead_rows / (live_rows + 1) > 0.2):  # >20% dead rows
                        self.results['recommendations'].append({
                            'type': 'table_bloat',
                            'severity': 'medium',
                            'object': f"{schema}.{table}",
                            'message': f'High number of dead rows ({dead_rows}). Consider VACUUM ANALYZE.'
                        })
                
        except Exception as e:
            self.logger.error(f"Table analysis failed: {e}")
            raise

    def analyze_index_usage(self) -> None:
        """Analyze index usage statistics."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        schemaname,
                        tablename,
                        indexrelname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch,
                        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                    FROM pg_stat_user_indexes
                    ORDER BY idx_scan DESC;
                """)
                
                for row in cur.fetchall():
                    schema, table, index, scans, reads, fetches, size = row
                    self.results['index_stats'][f"{schema}.{table}.{index}"] = {
                        'scans': scans,
                        'reads': reads,
                        'fetches': fetches,
                        'size': size
                    }
                    
                    # Check for unused indexes
                    if scans == 0 and size != '0 bytes':
                        self.results['recommendations'].append({
                            'type': 'unused_index',
                            'severity': 'medium',
                            'object': f"{schema}.{table}.{index}",
                            'message': f'Index is never used but occupies {size}. Consider dropping if not required.'
                        })
                    
        except Exception as e:
            self.logger.error(f"Index analysis failed: {e}")
            raise

    def analyze_slow_queries(self) -> None:
        """Analyze slow query statistics."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements
                    ORDER BY total_time DESC
                    LIMIT 10;
                """)
                
                for row in cur.fetchall():
                    query, calls, total_time, mean_time, rows = row
                    self.results['query_stats'][query] = {
                        'calls': calls,
                        'total_time': total_time,
                        'mean_time': mean_time,
                        'rows': rows
                    }
                    
                    # Check for slow queries
                    if mean_time > 1000:  # >1 second average
                        self.results['recommendations'].append({
                            'type': 'slow_query',
                            'severity': 'high',
                            'object': query[:100] + '...',
                            'message': f'Query is slow (avg {mean_time:.2f}ms). Consider optimization.'
                        })
                    
        except Exception as e:
            self.logger.error(f"Query analysis failed: {e}")
            raise

    def check_missing_indexes(self) -> None:
        """Check for potentially missing indexes."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        schemaname,
                        relname,
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch
                    FROM pg_stat_user_tables
                    WHERE seq_scan > 0
                    ORDER BY seq_tup_read DESC;
                """)
                
                for row in cur.fetchall():
                    schema, table, seq_scans, seq_reads, idx_scans, idx_fetches = row
                    
                    # Check for tables with high sequential scans
                    if seq_scans > 1000 and (idx_scans == 0 or (seq_scans / (idx_scans + 1) > 10)):
                        self.results['recommendations'].append({
                            'type': 'missing_index',
                            'severity': 'high',
                            'object': f"{schema}.{table}",
                            'message': f'High number of sequential scans ({seq_scans}). Consider adding indexes.'
                        })
                    
        except Exception as e:
            self.logger.error(f"Missing index analysis failed: {e}")
            raise

    def analyze_cache_hits(self) -> None:
        """Analyze database cache hit ratios."""
        try:
            with self.conn.cursor() as cur:
                # Check buffer cache hit ratio
                cur.execute("""
                    SELECT
                        sum(heap_blks_read) as heap_read,
                        sum(heap_blks_hit) as heap_hit,
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read))::float as ratio
                    FROM pg_statio_user_tables;
                """)
                
                heap_read, heap_hit, ratio = cur.fetchone()
                self.results['cache_stats'] = {
                    'heap_read': heap_read,
                    'heap_hit': heap_hit,
                    'hit_ratio': ratio
                }
                
                if ratio < 0.99:  # Less than 99% cache hit ratio
                    self.results['recommendations'].append({
                        'type': 'cache_ratio',
                        'severity': 'medium',
                        'object': 'buffer_cache',
                        'message': f'Low cache hit ratio ({ratio:.2%}). Consider increasing shared_buffers.'
                    })
                    
        except Exception as e:
            self.logger.error(f"Cache analysis failed: {e}")
            raise

    def generate_optimization_sql(self) -> None:
        """Generate SQL statements for recommended optimizations."""
        try:
            sql_file = Path('performance/sql/optimizations.sql')
            sql_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(sql_file, 'w') as f:
                f.write("-- Database Optimization SQL\n")
                f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
                
                # VACUUM ANALYZE statements
                for rec in self.results['recommendations']:
                    if rec['type'] == 'table_bloat':
                        f.write(f"VACUUM ANALYZE {rec['object']};\n")
                
                # Drop unused indexes
                for rec in self.results['recommendations']:
                    if rec['type'] == 'unused_index':
                        f.write(f"-- Consider: DROP INDEX {rec['object']};\n")
                
                # Add missing indexes (placeholder statements)
                for rec in self.results['recommendations']:
                    if rec['type'] == 'missing_index':
                        f.write(f"-- Consider: CREATE INDEX ON {rec['object']} (column_name);\n")
                
                self.logger.info(f"Optimization SQL generated: {sql_file}")
                
        except Exception as e:
            self.logger.error(f"SQL generation failed: {e}")
            raise

    def generate_report(self) -> None:
        """Generate a detailed optimization report."""
        try:
            report_dir = Path('performance/reports')
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / f"database_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            self.logger.info(f"""
            Database optimization analysis completed:
            - Tables analyzed: {len(self.results['table_stats'])}
            - Indexes analyzed: {len(self.results['index_stats'])}
            - Slow queries analyzed: {len(self.results['query_stats'])}
            - Recommendations: {len(self.results['recommendations'])}
            
            Report saved to: {report_file}
            """)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

    def optimize_database(self) -> None:
        """Run all database optimization tasks."""
        try:
            self.connect()
            
            self.analyze_table_stats()
            self.analyze_index_usage()
            self.analyze_slow_queries()
            self.check_missing_indexes()
            self.analyze_cache_hits()
            
            self.generate_optimization_sql()
            self.generate_report()
            
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python optimize_database.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    optimizer = DatabaseOptimizer(config_path)
    optimizer.optimize_database()

if __name__ == "__main__":
    main()
