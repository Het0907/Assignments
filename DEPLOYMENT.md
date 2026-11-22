# Deployment Guide: Rx Details Extractor

> **Complete deployment instructions for WSL, Docker, and Production environments**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (WSL/Linux)](#quick-start-wsllinux)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment (Systemd)](#production-deployment-systemd)
5. [Environment Configuration](#environment-configuration)
6. [Service Management](#service-management)
7. [Monitoring & Observability](#monitoring--observability)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.10+ | Backend runtime |
| **Docker** | 24+ | Container deployment |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | Latest | Repository cloning |
| **MongoDB** | 6.0+ | Job storage (or use Docker) |
| **RabbitMQ** | 3.12+ | Message broker (or use Docker) |

### Required Credentials

| File | Location | Purpose |
|------|----------|---------|
| `google_project_hermes.json` | `backend/app/core/` | GCP service account for Gemini AI & GCS |

> ⚠️ **Important:** Never commit credentials to version control.

---

## Quick Start (WSL/Linux)

### 1. Clone the Repository

```bash
git clone https://automationgit.meditab.com/ai/pharmacy/rx-details-extractor.git
cd rx-details-extractor
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create `backend/.env` file:

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS="app/core/google_project_hermes.json"
GOOGLE_CLOUD_PROJECT="meditab-autm-neutral-acent"

# GCS Bucket
GCS_BUCKET_NAME="rx-auto-typing-bucket"
GCS_LOCATION="us-central1"
GCS_STORAGE_CLASS="STANDARD"
GCS_LIFECYCLE_DELETE_DAYS=30

# Gemini AI
GEMINI_MODEL="gemini-3.1-pro-preview"
TEMPERATURE=1
THINKING_LEVEL="medium"

# API
API_PORT=8511

# MongoDB (local)
MONGO_URI="mongodb://localhost:27017"
MONGO_DB_NAME="rx_auto_typing_db"

# Celery (local RabbitMQ)
CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
CELERY_RESULT_DB="rx_auto_typing_results"
CELERY_TASK_LIMIT=600

# Authentication
AUTH_SERVICE_JWKS_URL="http://aibot.meditab.com/auth/.well-known/jwks.json"
AUTH_ALGORITHM="RS256"
AUTH_AUDIENCE="auth-service"
AUTH_ISSUER="auth-service"
```

### 4. Start Infrastructure Services

**Start MongoDB:**
```bash
# Using Docker
docker run -d --name mongodb -p 27017:27017 mongo:6.0

# Or install locally
sudo apt install mongodb
sudo systemctl start mongodb
```

**Start RabbitMQ:**
```bash
# Using Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Or install locally
sudo apt install rabbitmq-server
sudo systemctl start rabbitmq-server
```

### 5. Start the Application

**Terminal 1 - FastAPI Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8511 --reload
```

**Terminal 2 - Celery Extraction Worker:**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks.tasks.celery_app worker -Q RX_EXTRACTION --concurrency=4 -l info
```

**Terminal 3 - Celery Callback Worker:**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks.tasks.celery_app worker -Q RX_CALLBACK --concurrency=2 -l info
```

### 6. Verify Installation

```bash
# Health check
curl http://localhost:8511/rx/health
# Expected: {"status": "ok"}

# API docs
# Open: http://localhost:8511/rx/docs
```

---

## Docker Deployment

### 1. Navigate to Deployment Directory

```bash
cd deployment
```

### 2. Configure Environment for Docker

Update `backend/.env` for Docker networking:

```bash
# MongoDB (Docker service name)
MONGO_URI="mongodb://mongo:27017"

# RabbitMQ (Docker service name)
CELERY_BROKER_URL="amqp://guest:guest@rabbitmq:5672//"
```

### 3. Build and Start All Services

```bash
# Build and start all containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Docker Services Overview

| Service | Port | Description |
|---------|------|-------------|
| `backend` | 8504 | FastAPI application |
| `celery-priority` | — | High-priority extraction workers |
| `celery-batch` | — | Batch extraction workers |
| `mongo` | 27017 | MongoDB database |
| `rabbitmq` | 5672, 15672 | RabbitMQ broker + management UI |
| `loki` | 3100 | Log aggregation |
| `promtail` | — | Log collector |
| `grafana` | 3000 | Dashboards |
| `prometheus` | 9090 | Metrics |

### 5. Access Services

| Service | URL |
|---------|-----|
| **API** | http://localhost:8504/rx/health |
| **API Docs** | http://localhost:8504/rx/docs |
| **RabbitMQ Management** | http://localhost:15672 (guest/guest) |
| **Grafana** | http://localhost:3000 |
| **Prometheus** | http://localhost:9090 |

### 6. Stop Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Production Deployment (Systemd)

### 1. Create Project Directory

```bash
sudo mkdir -p /home/ai-automation@meditab.local/projects
cd /home/ai-automation@meditab.local/projects
git clone https://automationgit.meditab.com/ai/pharmacy/rx-details-extractor.git
cd rx-details-extractor/backend
```

### 2. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Systemd Service Files

```bash
# Copy service files
sudo cp deployment/services/rx-detail-extractor.service /etc/systemd/system/
sudo cp deployment/services/rx-main-celery.service /etc/systemd/system/
sudo cp deployment/services/rx-callback-celery.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload
```

### 4. Service File: FastAPI Backend

`/etc/systemd/system/rx-detail-extractor.service`:
```ini
[Unit]
Description=Rx Details Extractor API
After=network-online.target
Wants=network-online.target

[Service]
User=root
WorkingDirectory=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/
Environment="PATH=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/venv/bin"
ExecStart=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8511
Restart=always
RestartSec=5
StandardOutput=append:/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/logs/rx-details-extractor.log
StandardError=append:/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/logs/rx-details-extractor_error.log

[Install]
WantedBy=multi-user.target
```

### 5. Service File: Celery Extraction Worker

`/etc/systemd/system/rx-main-celery.service`:
```ini
[Unit]
Description=Rx Extraction Celery Worker
After=network-online.target
Wants=network-online.target

[Service]
User=root
WorkingDirectory=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/
Environment="PATH=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/venv/bin"
ExecStart=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/venv/bin/celery -A app.tasks.tasks.celery_app worker -Q RX_EXTRACTION --concurrency=10 -l info
Restart=always
RestartSec=5
StandardOutput=append:/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/logs/rx-details-extractor_main.log
StandardError=append:/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/logs/rx-details-extractor_main_error.log

[Install]
WantedBy=multi-user.target
```

### 6. Service File: Celery Callback Worker

`/etc/systemd/system/rx-callback-celery.service`:
```ini
[Unit]
Description=Rx Callback Celery Worker
After=network-online.target
Wants=network-online.target

[Service]
User=root
WorkingDirectory=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/
Environment="PATH=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/venv/bin"
ExecStart=/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/venv/bin/celery -A app.tasks.tasks.celery_app worker -Q RX_CALLBACK --concurrency=2 -l info
Restart=always
RestartSec=5
StandardOutput=append:/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/logs/rx-details-extractor_callback.log
StandardError=append:/home/ai-automation@meditab.local/projects/rx-details-extractor/backend/logs/rx-details-extractor_callback_error.log

[Install]
WantedBy=multi-user.target
```

### 7. Enable and Start Services

```bash
# Enable services to start on boot
sudo systemctl enable rx-detail-extractor
sudo systemctl enable rx-main-celery
sudo systemctl enable rx-callback-celery

# Start services
sudo systemctl start rx-detail-extractor
sudo systemctl start rx-main-celery
sudo systemctl start rx-callback-celery

# Check status
sudo systemctl status rx-detail-extractor
sudo systemctl status rx-main-celery
sudo systemctl status rx-callback-celery
```

---
## Service Management

### Systemd Commands

```bash
# Start a service
sudo systemctl start rx-detail-extractor

# Stop a service
sudo systemctl stop rx-detail-extractor

# Restart a service
sudo systemctl restart rx-detail-extractor

# View status
sudo systemctl status rx-detail-extractor

# View logs
sudo journalctl -u rx-detail-extractor -f

# Reload after config changes
sudo systemctl daemon-reload
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Scale workers
docker-compose up -d --scale celery-batch=3

# Rebuild after code changes
docker-compose up -d --build
```

---

## Monitoring & Observability

### Log Locations

| Component | Log File |
|-----------|----------|
| FastAPI | `backend/logs/rx-details-extractor.log` |
| Celery Main | `backend/logs/rx-details-extractor_main.log` |
| Celery Callback | `backend/logs/rx-details-extractor_callback.log` |

### Grafana Dashboards

1. Access Grafana: http://localhost:3000
2. Default credentials: admin/admin
3. Add Loki data source: http://loki:3100
4. Import dashboards for log visualization

### Health Checks

```bash
# API health
curl http://localhost:8511/rx/health

# RabbitMQ status
curl -u guest:guest http://localhost:15672/api/overview

# MongoDB status
mongosh --eval "db.adminCommand('ping')"
```

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| `Connection refused` on MongoDB | MongoDB not running | `docker start mongodb` or `sudo systemctl start mongodb` |
| `Connection refused` on RabbitMQ | RabbitMQ not running | `docker start rabbitmq` or `sudo systemctl start rabbitmq-server` |
| `ModuleNotFoundError` | Virtual env not activated | `source venv/bin/activate` |
| `google.auth.exceptions.DefaultCredentialsError` | Missing credentials | Verify `google_project_hermes.json` path in `.env` |
| Celery tasks stuck in queue | Workers not running | Start Celery workers |
| `Permission denied` on logs | Log directory permissions | `chmod 755 backend/logs` |

### Debug Commands

```bash
# Check if ports are in use
sudo lsof -i :8511
sudo lsof -i :5672
sudo lsof -i :27017

# Test MongoDB connection
mongosh "mongodb://localhost:27017" --eval "db.adminCommand('ping')"

# Test RabbitMQ connection
curl -u guest:guest http://localhost:15672/api/healthchecks/node

# Check Celery worker status
celery -A app.tasks.tasks.celery_app inspect active

# View Celery queues
celery -A app.tasks.tasks.celery_app inspect active_queues
```

### Log Analysis

```bash
# View recent errors
grep -i error backend/logs/rx-details-extractor.log | tail -20

# Watch logs in real-time
tail -f backend/logs/rx-details-extractor.log

# Search for specific request
grep "a1d2830d-53c2-7258" backend/logs/*.log
```

---

## Quick Reference

### Start Everything (Development)

```bash
# Terminal 1: Infrastructure
docker run -d --name mongodb -p 27017:27017 mongo:6.0
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Terminal 2: API
cd backend && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8511 --reload

# Terminal 3: Extraction Worker
cd backend && source venv/bin/activate
celery -A app.tasks.tasks.celery_app worker -Q RX_EXTRACTION --concurrency=4 -l info

# Terminal 4: Callback Worker
cd backend && source venv/bin/activate
celery -A app.tasks.tasks.celery_app worker -Q RX_CALLBACK --concurrency=2 -l info
```

### Start Everything (Docker)

```bash
cd deployment
docker-compose up -d --build
docker-compose logs -f
```

### Start Everything (Production)

```bash
sudo systemctl start rx-detail-extractor
sudo systemctl start rx-main-celery
sudo systemctl start rx-callback-celery
```
