# HPCL Lead Intelligence - Production Deployment Guide

## Overview

This guide covers deploying the HPCL Lead Intelligence system in a production environment with systemd process management, automated backups, and monitoring.

## Architecture

The system consists of two main services:
- **API Server**: FastAPI application serving REST endpoints (port 8000)
- **Scraper Service**: Background service collecting lead data from various sources

Both services share a SQLite database (`hp_pulse.db`) and are managed by systemd for automatic restart and logging.

## Prerequisites

- Linux server (Ubuntu 20.04+ or similar)
- Python 3.11 or higher
- Sudo access for systemd configuration
- (Optional) Nginx for reverse proxy
- (Optional) Domain name and SSL certificate

## Quick Start

### 1. Installation

```bash
cd /path/to/IITR-HPCL-Scraper/Scraper
chmod +x deployment/scripts/*.sh
./deployment/scripts/install.sh
```

The install script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Initialize database
- ✅ Create necessary directories
- ✅ Generate systemd service files

### 2. Configure Environment

Edit the `.env` file with your settings:

```bash
nano .env
```

Key settings:
```env
# JWT Settings
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_PATH=hp_pulse.db

# CORS (frontend domains)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 3. Install Systemd Services

Run the commands provided by the install script:

```bash
# Create log directories
sudo mkdir -p /var/log/hpcl-scraper /var/log/hpcl-api
sudo chown $(whoami):$(whoami) /var/log/hpcl-scraper /var/log/hpcl-api

# Install service files
sudo cp /tmp/hpcl-scraper.service /etc/systemd/system/
sudo cp /tmp/hpcl-api.service /etc/systemd/system/

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable hpcl-scraper hpcl-api
sudo systemctl start hpcl-scraper hpcl-api
```

### 4. Verify Services

```bash
# Check service status
sudo systemctl status hpcl-api hpcl-scraper

# View logs
sudo journalctl -u hpcl-api -f
sudo journalctl -u hpcl-scraper -f

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Open in browser
```

## Service Management

### Start/Stop/Restart Services

```bash
# Start services
sudo systemctl start hpcl-api
sudo systemctl start hpcl-scraper

# Stop services
sudo systemctl stop hpcl-api
sudo systemctl stop hpcl-scraper

# Restart services
sudo systemctl restart hpcl-api
sudo systemctl restart hpcl-scraper

# Check status
sudo systemctl status hpcl-api hpcl-scraper
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u hpcl-api -f
sudo journalctl -u hpcl-scraper -f

# Last 100 lines
sudo journalctl -u hpcl-api -n 100
sudo journalctl -u hpcl-scraper -n 100

# Logs from specific time
sudo journalctl -u hpcl-api --since "1 hour ago"
sudo journalctl -u hpcl-api --since "2024-02-10 00:00:00"
```

## Backups

### Manual Backup

```bash
./deployment/scripts/backup.sh
```

This creates a timestamped backup in `data/backups/` containing:
- Database file
- Configuration (.env)
- Recent logs (last 7 days)

### Automated Daily Backups

Add to crontab:

```bash
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * cd /path/to/Scraper && ./deployment/scripts/backup.sh >> logs/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop services
sudo systemctl stop hpcl-api hpcl-scraper

# Extract backup
cd /path/to/Scraper
tar -xzf data/backups/hpcl_backup_YYYYMMDD_HHMMSS.tar.gz -C /tmp

# Restore files
cp /tmp/hpcl_backup_*/hp_pulse.db ./hp_pulse.db
cp /tmp/hpcl_backup_*/.env ./.env

# Restart services
sudo systemctl start hpcl-api hpcl-scraper
```

## Deployment & Updates

### Deploying Updates

```bash
chmod +x deployment/scripts/deploy.sh
./deployment/scripts/deploy.sh
```

The deploy script:
1. Creates a backup
2. Pulls latest code (if using git)
3. Updates dependencies
4. Restarts services
5. Verifies services are running

### Manual Update Process

```bash
# Stop services
sudo systemctl stop hpcl-api hpcl-scraper

# Backup current state
./deployment/scripts/backup.sh

# Update code
git pull  # if using git
# or manually copy updated files

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl start hpcl-api hpcl-scraper

# Verify
sudo systemctl status hpcl-api hpcl-scraper
```

## Nginx Reverse Proxy (Optional)

### Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### Configure Nginx

```bash
# Copy configuration
sudo cp deployment/nginx/hpcl-api.conf /etc/nginx/sites-available/hpcl-api

# Edit and set your domain
sudo nano /etc/nginx/sites-available/hpcl-api

# Enable site
sudo ln -s /etc/nginx/sites-available/hpcl-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Check if services are running
systemctl is-active hpcl-api hpcl-scraper
```

### Database Monitoring

```bash
# Database size
du -h hp_pulse.db

# Lead count
sqlite3 hp_pulse.db "SELECT COUNT(*) FROM leads;"

# Recent activity
sqlite3 hp_pulse.db "SELECT * FROM scrape_log ORDER BY scraped_at DESC LIMIT 5;"
```

### Resource Usage

```bash
# Check CPU and Memory
top
htop  # if installed

# Service-specific
systemctl status hpcl-api
systemctl status hpcl-scraper
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
sudo journalctl -u hpcl-api -n 50
sudo journalctl -u hpcl-scraper -n 50

# Check service file
sudo systemctl cat hpcl-api

# Verify paths
which python3
which uvicorn
```

### Database Locked

```bash
# Check if database is locked
lsof hp_pulse.db

# If needed, restart services
sudo systemctl restart hpcl-api hpcl-scraper
```

### API Not Accessible

```bash
# Check if API is listening
sudo netstat -tlnp | grep 8000
# or
sudo lsof -i :8000

# Check firewall
sudo ufw status

# Test locally
curl http://localhost:8000/health
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep -E "(scraper|uvicorn)"

# Restart services to clear memory
sudo systemctl restart hpcl-api hpcl-scraper
```

## Security Checklist

- [ ] Change JWT_SECRET_KEY in `.env`
- [ ] Set up firewall (ufw)
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure rate limiting in Nginx
- [ ] Restrict database file permissions
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## Performance Optimization

### Database Optimization

```bash
# Vacuum database periodically
sqlite3 hp_pulse.db "VACUUM;"

# Analyze for query optimization
sqlite3 hp_pulse.db "ANALYZE;"
```

### Log Rotation

Logs are automatically rotated by systemd. To configure:

```bash
sudo nano /etc/systemd/journald.conf

# Set:
SystemMaxUse=500M
SystemMaxFileSize=50M
```

## Production Checklist

- [ ] Services installed and running
- [ ] Environment variables configured
- [ ] Backups automated (cron job)
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Log rotation configured
- [ ] Test credentials changed
- [ ] Documentation reviewed

## Support & Maintenance

### Daily Tasks
- Monitor service status
- Check logs for errors
- Verify scraper is collecting data

### Weekly Tasks
- Review backup logs
- Check disk space
- Review error logs

### Monthly Tasks
- Update dependencies
- Review and analyze feedback data
- Database optimization (VACUUM)
- Security updates

**Last Updated**: 2026-02-08
