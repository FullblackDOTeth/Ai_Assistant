# Head AI Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Security Setup](#security-setup)
7. [Monitoring Setup](#monitoring-setup)
8. [Maintenance](#maintenance)

## Prerequisites

### System Requirements
- Linux/Unix server (Ubuntu 20.04 LTS recommended)
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 16+
- Nginx 1.18+

### Network Requirements
- Open ports:
  - 80/443 (HTTP/HTTPS)
  - 5432 (PostgreSQL)
  - 6379 (Redis)
  - 8000 (API)
  - 9090 (Prometheus)
  - 3000 (Grafana)

## Environment Setup

### Server Preparation
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv postgresql redis-server nginx

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

### SSL Certificate
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## Installation

### Application Setup
```bash
# Create application directory
sudo mkdir -p /opt/headai
sudo chown -R $USER:$USER /opt/headai

# Clone repository
git clone https://github.com/your-org/head-ai.git /opt/headai
cd /opt/headai

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install
```

### Service Setup
```bash
# Create systemd service for API
sudo nano /etc/systemd/system/headai-api.service

[Unit]
Description=Head AI API
After=network.target

[Service]
User=headai
Group=headai
WorkingDirectory=/opt/headai
Environment="PATH=/opt/headai/venv/bin"
ExecStart=/opt/headai/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable headai-api
sudo systemctl start headai-api
```

## Configuration

### Environment Variables
```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env

# Environment variables
DATABASE_URL=postgresql://user:password@localhost:5432/headai
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
API_KEY=your-api-key
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/headai

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        root /opt/headai/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Database Setup

### PostgreSQL Setup
```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE headai;
CREATE USER headai WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE headai TO headai;

# Run migrations
cd /opt/headai
source venv/bin/activate
alembic upgrade head
```

### Redis Setup
```bash
# Configure Redis
sudo nano /etc/redis/redis.conf

# Set password
requirepass your-redis-password

# Restart Redis
sudo systemctl restart redis
```

## Security Setup

### Firewall Configuration
```bash
# Configure UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### SSL Configuration
```bash
# Configure SSL parameters
sudo nano /etc/nginx/nginx.conf

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

## Monitoring Setup

### Prometheus Setup
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.30.3/prometheus-2.30.3.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
cd prometheus-*

# Configure Prometheus
nano prometheus.yml

scrape_configs:
  - job_name: 'headai'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Setup
```bash
# Install Grafana
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

## Maintenance

### Backup Procedures
```bash
# Database backup
pg_dump -U headai headai > backup.sql

# Application backup
tar -czf headai-backup.tar.gz /opt/headai

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d)
pg_dump -U headai headai > $BACKUP_DIR/db_$DATE.sql
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /opt/headai
```

### Update Procedures
```bash
# Update application
cd /opt/headai
git pull
source venv/bin/activate
pip install -r requirements.txt
npm install
npm run build

# Restart services
sudo systemctl restart headai-api
sudo systemctl restart nginx
```

### Monitoring Checks
```bash
# Check service status
sudo systemctl status headai-api
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Check logs
sudo journalctl -u headai-api
sudo tail -f /var/log/nginx/error.log
```
