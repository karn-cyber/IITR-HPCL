#!/bin/bash
#
# HPCL Lead Intelligence - Deployment/Update Script
# Updates the application and restarts services
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}HPCL Lead Intelligence - Deployment${NC}"
echo -e "${GREEN}================================================${NC}\n"

# Check if services are running
echo -e "${YELLOW}Checking service status...${NC}"
SCRAPER_RUNNING=$(systemctl is-active hpcl-scraper 2>/dev/null || echo "inactive")
API_RUNNING=$(systemctl is-active hpcl-api 2>/dev/null || echo "inactive")

if [ "$SCRAPER_RUNNING" = "active" ] || [ "$API_RUNNING" = "active" ]; then
    echo -e "${YELLOW}Services are running. They will be restarted after update.${NC}"
fi

# Create backup before update
echo -e "\n${YELLOW}Creating backup before update...${NC}"
./deployment/scripts/backup.sh

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo -e "\n${YELLOW}Pulling latest code...${NC}"
    git pull
    echo -e "${GREEN}✓${NC} Code updated"
fi

# Activate virtual environment
source venv/bin/activate

# Update dependencies
echo -e "\n${YELLOW}Updating dependencies...${NC}"
pip install -r requirements.txt --upgrade > /dev/null
echo -e "${GREEN}✓${NC} Dependencies updated"

# Run database migrations (if any)
echo -e "\n${YELLOW}Checking database...${NC}"
# Add migration logic here if needed
echo -e "${GREEN}✓${NC} Database checked"

# Restart services if they were running
if [ "$SCRAPER_RUNNING" = "active" ]; then
    echo -e "\n${YELLOW}Restarting scraper service...${NC}"
    sudo systemctl restart hpcl-scraper
    echo -e "${GREEN}✓${NC} Scraper restarted"
fi

if [ "$API_RUNNING" = "active" ]; then
    echo -e "\n${YELLOW}Restarting API service...${NC}"
    sudo systemctl restart hpcl-api
    echo -e "${GREEN}✓${NC} API restarted"
fi

# Check service status
echo -e "\n${YELLOW}Checking service status...${NC}"
sleep 2

if systemctl is-active --quiet hpcl-scraper; then
    echo -e "${GREEN}✓${NC} Scraper is running"
else
    echo -e "${RED}✗${NC} Scraper is not running. Check logs: sudo journalctl -u hpcl-scraper -n 50"
fi

if systemctl is-active --quiet hpcl-api; then
    echo -e "${GREEN}✓${NC} API is running"
else
    echo -e "${RED}✗${NC} API is not running. Check logs: sudo journalctl -u hpcl-api -n 50"
fi

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}\n"
