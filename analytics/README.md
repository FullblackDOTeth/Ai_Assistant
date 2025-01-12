# Head AI Analytics System

A comprehensive analytics and reporting system for monitoring and analyzing the Head AI platform's performance, usage, and business metrics.

## Features

### Analytics Service
- System metrics collection (CPU, memory, disk usage)
- API performance monitoring
- User activity tracking
- Model performance analytics
- Business insights generation

### Dashboard Service
- Real-time metrics visualization
- Interactive data exploration
- Customizable time ranges
- Multiple visualization types
- Auto-refreshing panels

### Reporting Service
- Automated report generation
- Multiple export formats (PDF, CSV)
- Email distribution
- S3 backup storage
- Custom report templates

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Database
DB_PASSWORD=your_db_password

# Redis
REDIS_PASSWORD=your_redis_password

# AWS
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# SMTP
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password

# Analytics
GA_TRACKING_ID=your_ga_id
MIXPANEL_TOKEN=your_mixpanel_token
```

3. Configure analytics settings in `config/analytics.json`:
- Database connection details
- Redis settings
- Metrics collection intervals
- Report schedules
- Alert thresholds
- Storage policies

## Usage

### Start Analytics Service
```bash
python services/analytics_service.py
```

### Launch Dashboard
```bash
python services/dashboard_service.py
```

### Generate Reports
```bash
python services/reporting_service.py
```

## Dashboard

The dashboard is accessible at `http://localhost:8050` and includes:

- System Performance Panel
- API Metrics Panel
- User Activity Panel
- Model Performance Panel
- Business Insights Panel

## Reports

### Available Reports
1. Performance Report
   - System metrics
   - API performance
   - User activity
   - Model performance

2. Business Report
   - User growth
   - Usage trends
   - Performance analysis
   - Cost analysis

3. Custom Reports
   - Select specific metrics
   - Choose timeframe
   - Custom visualizations

### Export Formats
- PDF (formatted reports)
- CSV (raw data)
- JSON (programmatic access)

## Monitoring

### Metrics Collection
- Real-time system metrics
- API performance metrics
- User behavior metrics
- Model performance metrics
- Business metrics

### Alerting
- Resource usage alerts
- Performance degradation alerts
- Error rate alerts
- Business metric alerts

## Storage

### Data Retention
- Raw metrics: 90 days
- Aggregated data: 365 days
- Reports: 180 days

### Backup
- Automated S3 backups
- Configurable backup schedule
- Encryption at rest

## Security

- Environment variable configuration
- Encrypted data storage
- Secure API endpoints
- Access control
- Audit logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
