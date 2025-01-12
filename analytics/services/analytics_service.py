#!/usr/bin/env python3

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
import psutil
import requests
from fastapi import FastAPI, HTTPException
from redis import Redis

class AnalyticsService:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.db_engine = self._setup_database()
        self.redis_client = self._setup_redis()
        self.metrics_registry = CollectorRegistry()
        self._setup_metrics()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for analytics service."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('analytics.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('AnalyticsService')

    def _load_config(self, config_path: str) -> Dict:
        """Load analytics configuration."""
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
        return Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            password=redis_config['password'],
            db=redis_config.get('db', 0)
        )

    def _setup_metrics(self):
        """Set up Prometheus metrics."""
        self.metrics = {
            'api_requests': Counter(
                'api_requests_total',
                'Total API requests',
                ['endpoint', 'method', 'status'],
                registry=self.metrics_registry
            ),
            'response_time': Histogram(
                'response_time_seconds',
                'Response time in seconds',
                ['endpoint'],
                registry=self.metrics_registry
            ),
            'active_users': Gauge(
                'active_users',
                'Number of active users',
                registry=self.metrics_registry
            ),
            'model_predictions': Counter(
                'model_predictions_total',
                'Total model predictions',
                ['model', 'status'],
                registry=self.metrics_registry
            ),
            'system_memory': Gauge(
                'system_memory_usage_bytes',
                'System memory usage in bytes',
                registry=self.metrics_registry
            )
        }

    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system performance metrics."""
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv
            }
            
            # Update Prometheus metrics
            self.metrics['system_memory'].set(psutil.virtual_memory().used)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
            raise

    def collect_api_metrics(self, timeframe: str = '24h') -> Dict[str, Dict]:
        """Collect API usage metrics."""
        try:
            query = """
                SELECT 
                    endpoint,
                    method,
                    status,
                    COUNT(*) as count,
                    AVG(response_time) as avg_response_time,
                    MAX(response_time) as max_response_time,
                    MIN(response_time) as min_response_time
                FROM api_logs
                WHERE timestamp >= NOW() - INTERVAL :timeframe
                GROUP BY endpoint, method, status
            """
            
            with self.db_engine.connect() as conn:
                result = conn.execute(
                    text(query),
                    {'timeframe': timeframe}
                )
                metrics = {}
                for row in result:
                    endpoint = row.endpoint
                    if endpoint not in metrics:
                        metrics[endpoint] = {
                            'total_requests': 0,
                            'success_rate': 0,
                            'avg_response_time': 0,
                            'methods': {}
                        }
                    
                    metrics[endpoint]['total_requests'] += row.count
                    metrics[endpoint]['methods'][row.method] = row.count
                    metrics[endpoint]['avg_response_time'] = row.avg_response_time
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to collect API metrics: {str(e)}")
            raise

    def collect_user_metrics(self, timeframe: str = '24h') -> Dict[str, int]:
        """Collect user activity metrics."""
        try:
            query = """
                SELECT 
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(DISTINCT session_id) as total_sessions,
                    AVG(session_duration) as avg_session_duration
                FROM user_sessions
                WHERE start_time >= NOW() - INTERVAL :timeframe
            """
            
            with self.db_engine.connect() as conn:
                result = conn.execute(
                    text(query),
                    {'timeframe': timeframe}
                ).first()
                
                metrics = {
                    'active_users': result.active_users,
                    'total_sessions': result.total_sessions,
                    'avg_session_duration': result.avg_session_duration
                }
                
                # Update Prometheus metrics
                self.metrics['active_users'].set(result.active_users)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to collect user metrics: {str(e)}")
            raise

    def collect_model_metrics(self, timeframe: str = '24h') -> Dict[str, Dict]:
        """Collect model performance metrics."""
        try:
            query = """
                SELECT 
                    model_name,
                    COUNT(*) as total_predictions,
                    AVG(response_time) as avg_response_time,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_predictions
                FROM model_predictions
                WHERE timestamp >= NOW() - INTERVAL :timeframe
                GROUP BY model_name
            """
            
            with self.db_engine.connect() as conn:
                result = conn.execute(
                    text(query),
                    {'timeframe': timeframe}
                )
                
                metrics = {}
                for row in result:
                    metrics[row.model_name] = {
                        'total_predictions': row.total_predictions,
                        'success_rate': row.successful_predictions / row.total_predictions,
                        'avg_response_time': row.avg_response_time,
                        'avg_confidence': row.avg_confidence
                    }
                    
                    # Update Prometheus metrics
                    self.metrics['model_predictions'].labels(
                        model=row.model_name,
                        status='success'
                    ).inc(row.successful_predictions)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to collect model metrics: {str(e)}")
            raise

    def generate_performance_report(self, timeframe: str = '24h') -> Dict:
        """Generate comprehensive performance report."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'system_metrics': self.collect_system_metrics(),
                'api_metrics': self.collect_api_metrics(timeframe),
                'user_metrics': self.collect_user_metrics(timeframe),
                'model_metrics': self.collect_model_metrics(timeframe)
            }
            
            # Cache report
            cache_key = f"performance_report:{timeframe}"
            self.redis_client.setex(
                cache_key,
                timedelta(hours=1),
                json.dumps(report)
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {str(e)}")
            raise

    def generate_business_insights(self, timeframe: str = '30d') -> Dict:
        """Generate business insights and trends."""
        try:
            query = """
                SELECT 
                    DATE_TRUNC('day', timestamp) as date,
                    COUNT(DISTINCT user_id) as daily_users,
                    COUNT(*) as total_requests,
                    SUM(compute_cost) as compute_cost,
                    AVG(response_time) as avg_response_time
                FROM api_logs
                WHERE timestamp >= NOW() - INTERVAL :timeframe
                GROUP BY DATE_TRUNC('day', timestamp)
                ORDER BY date
            """
            
            df = pd.read_sql(
                text(query),
                self.db_engine,
                params={'timeframe': timeframe}
            )
            
            insights = {
                'user_growth': {
                    'current': int(df['daily_users'].iloc[-1]),
                    'growth': float(df['daily_users'].pct_change().mean()),
                    'trend': df['daily_users'].tolist()
                },
                'usage_trends': {
                    'daily_average': float(df['total_requests'].mean()),
                    'peak_usage': int(df['total_requests'].max()),
                    'trend': df['total_requests'].tolist()
                },
                'performance_trends': {
                    'response_time_avg': float(df['avg_response_time'].mean()),
                    'response_time_trend': df['avg_response_time'].tolist()
                },
                'cost_analysis': {
                    'total_cost': float(df['compute_cost'].sum()),
                    'daily_average': float(df['compute_cost'].mean()),
                    'trend': df['compute_cost'].tolist()
                }
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to generate business insights: {str(e)}")
            raise

    def export_report(self, report_type: str, format: str = 'json') -> str:
        """Export analytics report in specified format."""
        try:
            if report_type == 'performance':
                data = self.generate_performance_report()
            elif report_type == 'business':
                data = self.generate_business_insights()
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            if format == 'json':
                return json.dumps(data, indent=2)
            elif format == 'csv':
                df = pd.DataFrame(data)
                return df.to_csv(index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            self.logger.error(f"Failed to export report: {str(e)}")
            raise

def main():
    """Main entry point for analytics service."""
    try:
        service = AnalyticsService('config/analytics.json')
        
        # Generate and export reports
        performance_report = service.generate_performance_report()
        business_insights = service.generate_business_insights()
        
        print("Analytics service running successfully")
        print(f"Generated reports: {performance_report.keys()}")
        print(f"Generated insights: {business_insights.keys()}")
        
    except Exception as e:
        print(f"Analytics service failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
