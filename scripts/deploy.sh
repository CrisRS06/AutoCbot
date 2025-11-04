#!/bin/bash
# deploy.sh - Complete VPS deployment for Freqtrade
# Run on Ubuntu 22.04 LTS

set -e  # Exit on error

echo "========================================="
echo "FREQTRADE VPS DEPLOYMENT"
echo "========================================="

# Configuration
FREQTRADE_USER="freqtrade"
VPS_REGION="tokyo"  # For lowest latency to Binance

# ========== 1. SYSTEM UPDATE ==========
echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# ========== 2. INSTALL DEPENDENCIES ==========
echo "Installing dependencies..."
sudo apt-get install -y \
    python3-pip python3-venv python3-dev \
    git curl wget build-essential \
    fail2ban ufw

# ========== 3. CREATE USER ==========
if ! id "$FREQTRADE_USER" &>/dev/null; then
    echo "Creating freqtrade user..."
    sudo adduser --disabled-password --gecos "" $FREQTRADE_USER
    sudo usermod -aG sudo $FREQTRADE_USER
fi

# ========== 4. CONFIGURE FIREWALL ==========
echo "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw --force enable

# ========== 5. CONFIGURE FAIL2BAN ==========
echo "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# ========== 6. INSTALL FREQTRADE ==========
echo "Installing Freqtrade..."
sudo -u $FREQTRADE_USER bash << 'EOF'
cd /home/freqtrade
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
git checkout stable
./setup.sh -i
EOF

# ========== 7. CREATE SYSTEMD SERVICE ==========
echo "Creating systemd service..."
cat << 'EOF' | sudo tee /etc/systemd/system/freqtrade.service
[Unit]
Description=Freqtrade Trading Bot
After=network.target

[Service]
Type=simple
User=freqtrade
WorkingDirectory=/home/freqtrade/freqtrade
ExecStart=/home/freqtrade/freqtrade/.venv/bin/freqtrade trade \
    --config /home/freqtrade/freqtrade/user_data/config.json \
    --strategy MeanReversionML \
    --db-url sqlite:////home/freqtrade/freqtrade/user_data/tradesv3.sqlite

Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# ========== 8. CREATE BACKUP SCRIPT ==========
echo "Creating backup script..."
sudo -u $FREQTRADE_USER bash << 'EOF'
mkdir -p /home/freqtrade/backups

cat > /home/freqtrade/backup.sh << 'BACKUP_EOF'
#!/bin/bash
BACKUP_DIR="/home/freqtrade/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cd /home/freqtrade/freqtrade/user_data
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" \
    config.json strategies/ tradesv3.sqlite
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete
BACKUP_EOF

chmod +x /home/freqtrade/backup.sh
EOF

# Add to crontab
(crontab -u $FREQTRADE_USER -l 2>/dev/null; echo "0 2 * * * /home/freqtrade/backup.sh") | crontab -u $FREQTRADE_USER -

echo "========================================="
echo "DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Copy config.json to /home/freqtrade/freqtrade/user_data/"
echo "2. Copy strategies to /home/freqtrade/freqtrade/user_data/strategies/"
echo "3. Start bot: sudo systemctl start freqtrade"
echo "4. Check status: sudo systemctl status freqtrade"
echo "5. View logs: journalctl -u freqtrade -f"
