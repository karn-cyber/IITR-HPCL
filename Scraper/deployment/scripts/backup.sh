#!/bin/bash
#
# HPCL Lead Intelligence - Backup Script
# Backs up database and configuration files
#

set -e

# Configuration
BACKUP_DIR="data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="hpcl_backup_${TIMESTAMP}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create temporary backup directory
TEMP_BACKUP="/tmp/${BACKUP_NAME}"
mkdir -p "$TEMP_BACKUP"

# Backup database
echo -e "${YELLOW}Backing up database...${NC}"
if [ -f "hp_pulse.db" ]; then
    cp hp_pulse.db "$TEMP_BACKUP/"
    echo -e "${GREEN}✓${NC} Database backed up"
else
    echo -e "${YELLOW}⚠  Database not found${NC}"
fi

# Backup .env (with sensitive data warning)
echo -e "${YELLOW}Backing up configuration...${NC}"
if [ -f ".env" ]; then
    cp .env "$TEMP_BACKUP/"
    echo -e "${GREEN}✓${NC} Configuration backed up"
fi

# Backup logs (last 7 days)
echo -e "${YELLOW}Backing up recent logs...${NC}"
if [ -d "logs" ]; then
    find logs -type f -mtime -7 -exec cp {} "$TEMP_BACKUP/" \;
    echo -e "${GREEN}✓${NC} Logs backed up"
fi

# Create tarball
echo -e "${YELLOW}Creating archive...${NC}"
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C /tmp "${BACKUP_NAME}"
echo -e "${GREEN}✓${NC} Archive created: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Cleanup
rm -rf "$TEMP_BACKUP"

# Delete old backups (keep last 30 days)
echo -e "${YELLOW}Cleaning old backups...${NC}"
find "$BACKUP_DIR" -name "hpcl_backup_*.tar.gz" -mtime +30 -delete
echo -e "${GREEN}✓${NC} Old backups cleaned"

echo -e "\n${GREEN}Backup completed successfully!${NC}"
echo -e "Backup file: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Show backup size
SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo -e "Size: $SIZE"
