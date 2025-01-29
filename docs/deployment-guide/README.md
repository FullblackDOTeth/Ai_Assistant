# Deployment Guide

This guide provides comprehensive instructions for deploying the Head AI system in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Options](#deployment-options)
4. [Configuration](#configuration)
5. [Monitoring](#monitoring)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Hardware**:
  - CPU: 8+ cores
  - RAM: 16GB+ (32GB recommended)
  - Storage: 100GB+ SSD
  - Network: 1Gbps+

- **Software**:
  - Docker 20.10+
  - Kubernetes 1.24+
  - Helm 3.8+
  - PostgreSQL 14+
  - Redis 6+
  - Python 3.11+
  - Node.js 18+

### Cloud Provider Requirements

- **AWS**:
  - EKS cluster
  - RDS PostgreSQL
  - ElastiCache Redis
  - S3 bucket
  - Route 53 domain

- **Azure**:
  - AKS cluster
  - Azure Database for PostgreSQL
  - Azure Cache for Redis
  - Azure Blob Storage
  - Azure DNS

- **GCP**:
  - GKE cluster
  - Cloud SQL
  - Memorystore
  - Cloud Storage
  - Cloud DNS

## Environment Setup

### Development

1. Local setup:
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/head-ai.git
   cd head-ai

   # Install dependencies
   python -m pip install -r requirements.txt

   # Set up environment
   cp .env.example .env
   # Edit .env with development settings

   # Start services
   docker-compose up -d
   ```

### Staging

1. Infrastructure setup:
   ```bash
   # Navigate to terraform directory
   cd deployment/terraform/staging

   # Initialize terraform
   terraform init

   # Apply configuration
   terraform apply
   ```

2. Application deployment:
   ```bash
   # Navigate to helm directory
   cd deployment/helm

   # Install chart
   helm upgrade --install head-ai ./head-ai \
     --namespace staging \
     --values values-staging.yaml
   ```

### Production

1. Infrastructure setup:
   ```bash
   # Navigate to terraform directory
   cd deployment/terraform/production

   # Initialize terraform
   terraform init

   # Apply configuration
   terraform apply
   ```

2. Application deployment:
   ```bash
   # Navigate to helm directory
   cd deployment/helm

   # Install chart
   helm upgrade --install head-ai ./head-ai \
     --namespace production \
     --values values-production.yaml
   ```

## Deployment Options

### Docker Compose

Suitable for development and small deployments:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/headai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=headai

  redis:
    image: redis:6
```

### Kubernetes

Recommended for production deployments:

1. Create namespace:
   ```bash
   kubectl create namespace head-ai
   ```

2. Apply configurations:
   ```bash
   # Apply secrets
   kubectl apply -f deployment/k8s/secrets.yaml

   # Apply configmaps
   kubectl apply -f deployment/k8s/configmaps.yaml

   # Deploy application
   kubectl apply -f deployment/k8s/
   ```

### Serverless

For specific components that benefit from serverless architecture:

- AWS Lambda functions
- Azure Functions
- Google Cloud Functions

## Configuration

### Environment Variables

Essential configuration parameters:

```bash
# Application
APP_NAME=head-ai
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://host:6379/0
REDIS_POOL_SIZE=100

# Security
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_TIMEOUT=60

# AI Model
MODEL_PATH=/path/to/model
MODEL_DEVICE=cuda
MODEL_BATCH_SIZE=32

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### Security Configuration

1. SSL/TLS setup:
   ```bash
   # Generate certificate
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout private.key -out certificate.crt

   # Configure in nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/nginx/certs/certificate.crt;
       ssl_certificate_key /etc/nginx/certs/private.key;
   }
   ```

2. Firewall rules:
   ```bash
   # Allow necessary ports
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 8000/tcp
   ```

## Monitoring

### Prometheus Setup

1. Deploy Prometheus:
   ```bash
   helm repo add prometheus-community \
     https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/prometheus
   ```

2. Configure scraping:
   ```yaml
   scrape_configs:
     - job_name: 'head-ai'
       static_configs:
         - targets: ['head-ai:8000']
   ```

### Grafana Setup

1. Deploy Grafana:
   ```bash
   helm repo add grafana https://grafana.github.io/helm-charts
   helm install grafana grafana/grafana
   ```

2. Import dashboards:
   ```bash
   # Get admin password
   kubectl get secret grafana -o jsonpath="{.data.admin-password}" \
     | base64 --decode

   # Access Grafana UI and import dashboards
   ```

## Maintenance

### Backup Procedures

1. Database backup:
   ```bash
   # Automated backup script
   #!/bin/bash
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > \
     backup_${TIMESTAMP}.sql
   ```

2. Application backup:
   ```bash
   # Backup persistent volumes
   kubectl get pv -o yaml > pv_backup.yaml
   kubectl get pvc -o yaml > pvc_backup.yaml
   ```

### Updates

1. Rolling updates:
   ```bash
   # Update deployment
   kubectl set image deployment/head-ai \
     head-ai=head-ai:new-version

   # Monitor rollout
   kubectl rollout status deployment/head-ai
   ```

2. Database migrations:
   ```bash
   # Run migrations
   alembic upgrade head

   # Verify migration status
   alembic current
   ```

## Troubleshooting

### Common Issues

1. Database connection issues:
   ```bash
   # Check database status
   kubectl exec -it pod/postgres-0 -- psql -U postgres

   # View logs
   kubectl logs deployment/head-ai
   ```

2. Application errors:
   ```bash
   # View application logs
   kubectl logs -f deployment/head-ai

   # Check pod status
   kubectl describe pod head-ai
   ```

3. Performance issues:
   ```bash
   # Monitor resources
   kubectl top pods
   kubectl top nodes

   # View metrics in Grafana
   ```

### Support

For deployment support:

1. Check documentation
2. Review logs
3. Contact DevOps team
4. Create support ticket

## Security Considerations

1. Network security:
   - Use VPC/subnet isolation
   - Implement security groups
   - Enable WAF protection

2. Access control:
   - Use RBAC
   - Implement least privilege
   - Regular access reviews

3. Monitoring:
   - Enable audit logging
   - Set up alerts
   - Regular security scans
