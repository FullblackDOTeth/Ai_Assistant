#!/usr/bin/env python3

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import boto3
from analytics_service import AnalyticsService

class ReportingService:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.analytics = AnalyticsService(config_path)
        self.template_env = self._setup_templates()
        self.s3 = self._setup_s3()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for reporting service."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('reporting.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('ReportingService')

    def _load_config(self, config_path: str) -> Dict:
        """Load reporting configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _setup_templates(self) -> Environment:
        """Set up Jinja2 template environment."""
        return Environment(
            loader=FileSystemLoader('templates/reports'),
            autoescape=True
        )

    def _setup_s3(self):
        """Set up S3 client for report storage."""
        return boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.config['aws']['region']
        )

    def generate_performance_report(self, timeframe: str = '24h') -> Dict:
        """Generate performance report with all metrics."""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'system_metrics': self.analytics.collect_system_metrics(),
                'api_metrics': self.analytics.collect_api_metrics(timeframe),
                'user_metrics': self.analytics.collect_user_metrics(timeframe),
                'model_metrics': self.analytics.collect_model_metrics(timeframe)
            }
            
            template = self.template_env.get_template('performance_report.html')
            report_html = template.render(data=report_data)
            
            return {
                'data': report_data,
                'html': report_html
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {str(e)}")
            raise

    def generate_business_report(self, timeframe: str = '30d') -> Dict:
        """Generate business insights report."""
        try:
            insights = self.analytics.generate_business_insights(timeframe)
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'insights': insights
            }
            
            template = self.template_env.get_template('business_report.html')
            report_html = template.render(data=report_data)
            
            return {
                'data': report_data,
                'html': report_html
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate business report: {str(e)}")
            raise

    def generate_custom_report(self, metrics: List[str], timeframe: str) -> Dict:
        """Generate custom report with specified metrics."""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'metrics': {}
            }
            
            for metric in metrics:
                if metric == 'system':
                    report_data['metrics']['system'] = self.analytics.collect_system_metrics()
                elif metric == 'api':
                    report_data['metrics']['api'] = self.analytics.collect_api_metrics(timeframe)
                elif metric == 'user':
                    report_data['metrics']['user'] = self.analytics.collect_user_metrics(timeframe)
                elif metric == 'model':
                    report_data['metrics']['model'] = self.analytics.collect_model_metrics(timeframe)
                elif metric == 'business':
                    report_data['metrics']['business'] = self.analytics.generate_business_insights(timeframe)
            
            template = self.template_env.get_template('custom_report.html')
            report_html = template.render(data=report_data)
            
            return {
                'data': report_data,
                'html': report_html
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate custom report: {str(e)}")
            raise

    def export_report_pdf(self, report: Dict, output_path: str) -> str:
        """Export report to PDF format."""
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8"
            }
            
            pdfkit.from_string(report['html'], output_path, options=options)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export PDF report: {str(e)}")
            raise

    def export_report_csv(self, report: Dict, output_path: str) -> str:
        """Export report data to CSV format."""
        try:
            df = pd.DataFrame.from_dict(report['data'], orient='index')
            df.to_csv(output_path)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV report: {str(e)}")
            raise

    def upload_to_s3(self, file_path: str, report_type: str) -> str:
        """Upload report to S3 bucket."""
        try:
            bucket = self.config['export']['scheduled']['destinations']['s3']['bucket']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            key = f"reports/{report_type}/{timestamp}_{os.path.basename(file_path)}"
            
            self.s3.upload_file(
                file_path,
                bucket,
                key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'ContentType': 'application/pdf' if file_path.endswith('.pdf') else 'text/csv'
                }
            )
            
            return f"s3://{bucket}/{key}"
            
        except Exception as e:
            self.logger.error(f"Failed to upload report to S3: {str(e)}")
            raise

    def send_email_report(self, report: Dict, recipients: List[str], subject: str):
        """Send report via email."""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.config['export']['scheduled']['destinations']['email']['from']
            msg['To'] = ', '.join(recipients)
            
            # Add HTML content
            msg.attach(MIMEText(report['html'], 'html'))
            
            # Export and attach PDF
            pdf_path = '/tmp/report.pdf'
            self.export_report_pdf(report, pdf_path)
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename='report.pdf'
                )
                msg.attach(pdf_attachment)
            
            # Send email
            with smtplib.SMTP(self.config['smtp']['host'], self.config['smtp']['port']) as server:
                server.starttls()
                server.login(
                    self.config['smtp']['username'],
                    self.config['smtp']['password']
                )
                server.send_message(msg)
            
        except Exception as e:
            self.logger.error(f"Failed to send email report: {str(e)}")
            raise

    def schedule_reports(self):
        """Schedule automated report generation and distribution."""
        try:
            schedule_config = self.config['export']['scheduled']
            if not schedule_config['enabled']:
                return
            
            # Generate reports
            performance_report = self.generate_performance_report('24h')
            business_report = self.generate_business_report('30d')
            
            # Export reports
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for format in schedule_config['formats']:
                if format == 'pdf':
                    # Export PDFs
                    perf_pdf = self.export_report_pdf(
                        performance_report,
                        f'/tmp/performance_{timestamp}.pdf'
                    )
                    biz_pdf = self.export_report_pdf(
                        business_report,
                        f'/tmp/business_{timestamp}.pdf'
                    )
                    
                    # Upload to S3
                    self.upload_to_s3(perf_pdf, 'performance')
                    self.upload_to_s3(biz_pdf, 'business')
                    
                elif format == 'csv':
                    # Export CSVs
                    perf_csv = self.export_report_csv(
                        performance_report,
                        f'/tmp/performance_{timestamp}.csv'
                    )
                    biz_csv = self.export_report_csv(
                        business_report,
                        f'/tmp/business_{timestamp}.csv'
                    )
                    
                    # Upload to S3
                    self.upload_to_s3(perf_csv, 'performance')
                    self.upload_to_s3(biz_csv, 'business')
            
            # Send email reports
            if schedule_config['destinations']['email']['enabled']:
                recipients = schedule_config['destinations']['email']['recipients']
                
                self.send_email_report(
                    performance_report,
                    recipients,
                    f"{schedule_config['destinations']['email']['subject_prefix']} Daily Performance Report"
                )
                
                self.send_email_report(
                    business_report,
                    recipients,
                    f"{schedule_config['destinations']['email']['subject_prefix']} Monthly Business Report"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to schedule reports: {str(e)}")
            raise

def main():
    """Main entry point for reporting service."""
    try:
        service = ReportingService('config/analytics.json')
        
        # Generate and distribute reports
        service.schedule_reports()
        
        print("Reporting service completed successfully")
        
    except Exception as e:
        print(f"Reporting service failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
