#!/bin/bash
#
# HPCL Lead Intelligence - Installation Script
# This script sets up the system for production deployment
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}HPCL Lead Intelligence - Installation${NC}"
echo -e "${GREEN}================================================${NC}\n"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run as root. Run as the user that will own the application.${NC}"
   exit 1
fi

# Get installation directory
INSTALL_DIR="$(pwd)"
echo -e "${YELLOW}Installation directory:${NC} $INSTALL_DIR"

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}Python 3.11+ is required. Current version: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null
echo -e "${GREEN}✓${NC} pip upgraded"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt > /dev/null
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p logs data/backups
echo -e "${GREEN}✓${NC} Directories created"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠  Please edit .env and set your configuration values${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Initialize database
echo -e "\n${YELLOW}Initializing database...${NC}"
if [ ! -f "hp_pulse.db" ]; then
    python3 backend/scripts/seed_data.py
    echo -e "${GREEN}✓${NC} Database initialized and seeded"
else
    echo -e "${YELLOW}⚠  Database already exists, skipping seed${NC}"
fi

# Set up systemd services (requires sudo)
echo -e "\n${YELLOW}Setting up systemd services...${NC}"
USER=$(whoami)

# Update service files with actual paths
sed -e "s|%USER%|$USER|g" \
    -e "s|%INSTALL_DIR%|$INSTALL_DIR|g" \
    deployment/systemd/hpcl-scraper.service > /tmp/hpcl-scraper.service

sed -e "s|%USER%|$USER|g" \
    -e "s|%INSTALL_DIR%|$INSTALL_DIR|g" \
    deployment/systemd/hpcl-api.service > /tmp/hpcl-api.service

echo -e "${YELLOW}To install systemd services, run these commands as root:${NC}"
echo ""
echo "  sudo mkdir -p /var/log/hpcl-scraper /var/log/hpcl-api"
echo "  sudo chown $USER:$USER /var/log/hpcl-scraper /var/log/hpcl-api"
echo "  sudo cp /tmp/hpcl-scraper.service /etc/systemd/system/"
echo "  sudo cp /tmp/hpcl-api.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable hpcl-scraper"
echo "  sudo systemctl enable hpcl-api"
echo "  sudo systemctl start hpcl-scraper"
echo "  sudo systemctl start hpcl-api"
echo ""

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}\n"

echo -e "Next steps:"
echo -e "  1. Edit ${YELLOW}.env${NC} with your configuration"
echo -e "  2. Run the systemd commands above to install services"
echo -e "  3. Check service status: ${YELLOW}sudo systemctl status hpcl-api hpcl-scraper${NC}"
echo -e "  4. View logs: ${YELLOW}sudo journalctl -u hpcl-api -f${NC}"
echo -e "  5. Access API: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
