#!/bin/bash
# SurBlend Installation Script for Raspberry Pi 5
# Run with: sudo bash install_surblend.sh

set -e  # Exit on error

echo "======================================"
echo "SurBlend Installation for Raspberry Pi"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
apt install -y \
    python3.11 python3.11-venv python3.11-dev \
    postgresql postgresql-contrib \
    nginx \
    git \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    supervisor

# Install Node.js 20.x for frontend
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Create application user
echo "Creating surblend user..."
useradd -m -s /bin/bash surblend || echo "User already exists"

# Create application directory
echo "Setting up application directory..."
mkdir -p /opt/surblend
chown -R surblend:surblend /opt/surblend

# Setup PostgreSQL
echo "Setting up PostgreSQL..."
sudo -u postgres psql << EOF
CREATE USER surblend WITH PASSWORD 'surblend123';
CREATE DATABASE surblend OWNER surblend;
GRANT ALL PRIVILEGES ON DATABASE surblend TO surblend;
EOF

# Configure PostgreSQL for local connections
echo "Configuring PostgreSQL..."
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+')
echo "host    surblend        surblend        127.0.0.1/32            md5" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
systemctl restart postgresql

# Create Python virtual environment
echo "Creating Python virtual environment..."
cd /opt/surblend
sudo -u surblend python3.11 -m venv venv

# Create .env file
echo "Creating environment file..."
cat > /opt/surblend/.env << 'EOL'
# SurBlend Environment Configuration
DATABASE_URL=postgresql://surblend:surblend123@localhost:5432/surblend
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_EMAIL=admin@surblend.local
ADMIN_PASSWORD=SurBlend2025!
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
HOST_IP=$(hostname -I | awk '{print $1}')
EOL

chown surblend:surblend /opt/surblend/.env
chmod 600 /opt/surblend/.env

# Create application structure
echo "Creating application structure..."
sudo -u surblend mkdir -p /opt/surblend/{backend,frontend,logs,uploads}

# Create systemd service for backend
echo "Creating systemd service..."
cat > /etc/systemd/system/surblend.service << 'EOL'
[Unit]
Description=SurBlend Backend Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=surblend
Group=surblend
WorkingDirectory=/opt/surblend/backend
Environment="PATH=/opt/surblend/venv/bin"
ExecStart=/opt/surblend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Create nginx configuration
echo "Configuring nginx..."
cat > /etc/nginx/sites-available/surblend << 'EOL'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /opt/surblend/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
    
    # Static files
    location /static {
        alias /opt/surblend/backend/static;
    }
    
    # Upload size limit
    client_max_body_size 10M;
}
EOL

# Enable nginx site
ln -sf /etc/nginx/sites-available/surblend /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Create log rotation
echo "Setting up log rotation..."
cat > /etc/logrotate.d/surblend << 'EOL'
/opt/surblend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 surblend surblend
    sharedscripts
    postrotate
        systemctl reload surblend.service > /dev/null 2>&1 || true
    endscript
}
EOL

# Create deployment script
echo "Creating deployment script..."
cat > /opt/surblend/deploy.sh << 'EOL'
#!/bin/bash
# SurBlend Deployment Script

cd /opt/surblend

# Backend deployment
echo "Deploying backend..."
cd backend
source ../venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Frontend deployment
echo "Deploying frontend..."
cd ../frontend
npm install
npm run build

# Restart services
echo "Restarting services..."
sudo systemctl daemon-reload
sudo systemctl restart surblend
sudo systemctl restart nginx

echo "Deployment complete!"
EOL

chmod +x /opt/surblend/deploy.sh
chown surblend:surblend /opt/surblend/deploy.sh

# Create backup script
echo "Creating backup script..."
cat > /opt/surblend/backup.sh << 'EOL'
#!/bin/bash
# SurBlend Backup Script

BACKUP_DIR="/opt/surblend/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
sudo -u postgres pg_dump surblend | gzip > $BACKUP_DIR/surblend_db_$TIMESTAMP.sql.gz

# Backup uploads
echo "Backing up uploads..."
tar -czf $BACKUP_DIR/surblend_uploads_$TIMESTAMP.tar.gz -C /opt/surblend uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup complete: $BACKUP_DIR"
EOL

chmod +x /opt/surblend/backup.sh
chown surblend:surblend /opt/surblend/backup.sh

# Add backup to crontab
echo "0 2 * * * /opt/surblend/backup.sh > /opt/surblend/logs/backup.log 2>&1" | crontab -u surblend -

# Create initial directory structure message
echo "Creating initial application files..."
cat > /opt/surblend/backend/app/__init__.py << 'EOL'
# SurBlend Backend Package
EOL

# Set permissions
chown -R surblend:surblend /opt/surblend
chmod -R 755 /opt/surblend

# Enable services
echo "Enabling services..."
systemctl daemon-reload
systemctl enable postgresql
systemctl enable nginx
systemctl enable surblend

# Performance optimization for Raspberry Pi
echo "Optimizing for Raspberry Pi..."
# Increase swap file size
dphys-swapfile swapoff
sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
dphys-swapfile setup
dphys-swapfile swapon

# Optimize PostgreSQL for Pi
cat >> /etc/postgresql/*/main/postgresql.conf << 'EOL'

# Raspberry Pi Optimizations
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB
max_connections = 50
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
EOL

systemctl restart postgresql

# Create quick start guide
cat > /opt/surblend/README.md << 'EOL'
# SurBlend Quick Start Guide

## Installation Complete!

### Default Credentials
- **Username**: admin
- **Password**: SurBlend2025!

### Access the Application
- **Web Interface**: http://YOUR_PI_IP_ADDRESS
- **API Documentation**: http://YOUR_PI_IP_ADDRESS/api/docs

### Important Commands

#### Start/Stop Services
```bash
sudo systemctl start surblend    # Start backend
sudo systemctl stop surblend     # Stop backend
sudo systemctl restart surblend  # Restart backend
sudo systemctl status surblend   # Check status
```

#### View Logs
```bash
sudo journalctl -u surblend -f  # Backend logs
sudo tail -f /var/log/nginx/error.log  # Nginx errors
```

#### Deploy Updates
```bash
cd /opt/surblend
sudo -u surblend ./deploy.sh
```

#### Create Backup
```bash
sudo -u surblend /opt/surblend/backup.sh
```

### Next Steps
1. Copy your application code to `/opt/surblend/backend/` and `/opt/surblend/frontend/`
2. Install Python dependencies: `cd /opt/surblend && sudo -u surblend venv/bin/pip install -r backend/requirements.txt`
3. Build frontend: `cd /opt/surblend/frontend && sudo -u surblend npm install && sudo -u surblend npm run build`
4. Run deployment script: `sudo -u surblend /opt/surblend/deploy.sh`

### System Information
- PostgreSQL Database: surblend
- Backend Port: 8000
- Frontend Port: 80
- Application User: surblend
- Application Directory: /opt/surblend

### Troubleshooting
- Check service status: `sudo systemctl status surblend`
- Check PostgreSQL: `sudo -u postgres psql -c "SELECT version();"`
- Test database connection: `sudo -u surblend psql -d surblend -c "SELECT 1;"`
- Check disk space: `df -h`
- Check memory: `free -h`

For support, check logs and ensure all services are running.
EOL

chown surblend:surblend /opt/surblend/README.md

# Final summary
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: SurBlend2025!"
echo ""
echo "Access the application at:"
echo "http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Next steps:"
echo "1. Copy your application code to /opt/surblend/"
echo "2. Run: sudo -u surblend /opt/surblend/deploy.sh"
echo ""
echo "See /opt/surblend/README.md for more information"
echo ""