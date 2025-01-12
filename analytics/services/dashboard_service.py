#!/usr/bin/env python3

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from analytics_service import AnalyticsService

class DashboardService:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.analytics = AnalyticsService(config_path)
        self.app = self._setup_dashboard()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for dashboard service."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('dashboard.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('DashboardService')

    def _load_config(self, config_path: str) -> Dict:
        """Load dashboard configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _setup_dashboard(self) -> dash.Dash:
        """Initialize and configure Dash application."""
        app = dash.Dash(__name__)
        
        app.layout = html.Div([
            # Header
            html.Div([
                html.H1('Head AI Analytics Dashboard'),
                html.Div([
                    dcc.Dropdown(
                        id='timeframe-selector',
                        options=[
                            {'label': 'Last 24 Hours', 'value': '24h'},
                            {'label': 'Last 7 Days', 'value': '7d'},
                            {'label': 'Last 30 Days', 'value': '30d'},
                            {'label': 'Last 90 Days', 'value': '90d'}
                        ],
                        value='24h'
                    )
                ])
            ], className='header'),
            
            # System Metrics
            html.Div([
                html.H2('System Performance'),
                dcc.Graph(id='system-metrics-graph')
            ], className='panel'),
            
            # API Metrics
            html.Div([
                html.H2('API Performance'),
                dcc.Graph(id='api-metrics-graph')
            ], className='panel'),
            
            # User Metrics
            html.Div([
                html.H2('User Activity'),
                dcc.Graph(id='user-metrics-graph')
            ], className='panel'),
            
            # Model Metrics
            html.Div([
                html.H2('Model Performance'),
                dcc.Graph(id='model-metrics-graph')
            ], className='panel'),
            
            # Business Insights
            html.Div([
                html.H2('Business Insights'),
                dcc.Graph(id='business-insights-graph')
            ], className='panel'),
            
            # Update interval
            dcc.Interval(
                id='interval-component',
                interval=self.config['dashboards']['refresh_interval'] * 1000,
                n_intervals=0
            )
        ])
        
        self._setup_callbacks(app)
        return app

    def _setup_callbacks(self, app: dash.Dash):
        """Set up dashboard callbacks."""
        @app.callback(
            [Output('system-metrics-graph', 'figure'),
             Output('api-metrics-graph', 'figure'),
             Output('user-metrics-graph', 'figure'),
             Output('model-metrics-graph', 'figure'),
             Output('business-insights-graph', 'figure')],
            [Input('timeframe-selector', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_graphs(timeframe: str, n_intervals: int):
            try:
                # Get metrics
                system_metrics = self.analytics.collect_system_metrics()
                api_metrics = self.analytics.collect_api_metrics(timeframe)
                user_metrics = self.analytics.collect_user_metrics(timeframe)
                model_metrics = self.analytics.collect_model_metrics(timeframe)
                business_insights = self.analytics.generate_business_insights(timeframe)
                
                # Create system metrics figure
                system_fig = make_subplots(rows=2, cols=2)
                system_fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=system_metrics['cpu_percent'],
                        title={'text': "CPU Usage (%)"},
                        gauge={'axis': {'range': [0, 100]}}
                    ),
                    row=1, col=1
                )
                system_fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=system_metrics['memory_percent'],
                        title={'text': "Memory Usage (%)"},
                        gauge={'axis': {'range': [0, 100]}}
                    ),
                    row=1, col=2
                )
                system_fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=system_metrics['disk_percent'],
                        title={'text': "Disk Usage (%)"},
                        gauge={'axis': {'range': [0, 100]}}
                    ),
                    row=2, col=1
                )
                
                # Create API metrics figure
                api_df = pd.DataFrame(api_metrics).transpose()
                api_fig = px.bar(
                    api_df,
                    x=api_df.index,
                    y='total_requests',
                    title='API Requests by Endpoint'
                )
                
                # Create user metrics figure
                user_fig = make_subplots(specs=[[{"secondary_y": True}]])
                user_fig.add_trace(
                    go.Scatter(
                        x=['Active Users', 'Total Sessions'],
                        y=[user_metrics['active_users'], user_metrics['total_sessions']],
                        name="Counts"
                    )
                )
                user_fig.add_trace(
                    go.Scatter(
                        x=['Active Users', 'Total Sessions'],
                        y=[user_metrics['avg_session_duration']],
                        name="Avg Duration",
                        yaxis="y2"
                    ),
                    secondary_y=True
                )
                
                # Create model metrics figure
                model_df = pd.DataFrame(model_metrics).transpose()
                model_fig = px.scatter(
                    model_df,
                    x='avg_response_time',
                    y='success_rate',
                    size='total_predictions',
                    hover_data=['avg_confidence'],
                    title='Model Performance'
                )
                
                # Create business insights figure
                business_fig = make_subplots(rows=2, cols=2)
                business_fig.add_trace(
                    go.Scatter(
                        x=list(range(len(business_insights['user_growth']['trend']))),
                        y=business_insights['user_growth']['trend'],
                        name='User Growth'
                    ),
                    row=1, col=1
                )
                business_fig.add_trace(
                    go.Scatter(
                        x=list(range(len(business_insights['usage_trends']['trend']))),
                        y=business_insights['usage_trends']['trend'],
                        name='Usage Trend'
                    ),
                    row=1, col=2
                )
                business_fig.add_trace(
                    go.Scatter(
                        x=list(range(len(business_insights['cost_analysis']['trend']))),
                        y=business_insights['cost_analysis']['trend'],
                        name='Cost Trend'
                    ),
                    row=2, col=1
                )
                
                return system_fig, api_fig, user_fig, model_fig, business_fig
                
            except Exception as e:
                self.logger.error(f"Failed to update graphs: {str(e)}")
                raise

    def run(self, host: str = '0.0.0.0', port: int = 8050, debug: bool = False):
        """Run the dashboard server."""
        try:
            self.logger.info(f"Starting dashboard server on {host}:{port}")
            self.app.run_server(host=host, port=port, debug=debug)
            
        except Exception as e:
            self.logger.error(f"Failed to start dashboard server: {str(e)}")
            raise

def main():
    """Main entry point for dashboard service."""
    try:
        service = DashboardService('config/analytics.json')
        service.run()
        
    except Exception as e:
        print(f"Dashboard service failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
