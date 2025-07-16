#!/bin/bash
# Health check script for SurBlend

set -e

echo "=== SurBlend Health Check ==="
echo "Time: $(date)"
echo ""

# Function to check service
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
        return 0
    else
        echo "✗ $service is not running"
        return 1
    fi
}

# Function to check port
check_port() {
    local port=$1
    local service=$2
    if nc -z localhost $port 2>/dev/null; then
        echo "✓ Port $port ($service) is open"
        return 0
    else
        echo "✗ Port $port ($service) is not accessible"
        return 1
    fi
}

# Function to check database
check_database() {
    if sudo -u surblend psql -d surblend -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✓ Database connection successful"
        # Get database size
        local db_size=$(sudo -u postgres psql -t -c "SELECT pg_size_pretty(pg_database_size('surblend'));" surblend | tr -d ' ')
        echo "  Database size: $db_size"
        return 0
    else
        echo "✗ Database connection failed"
        return 1
    fi
}

# Function to check API
check_api() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$response" = "200" ]; then
        echo "✓ API health check passed"
        return 0
    else
        echo "✗ API health check failed (HTTP $response)"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $usage -lt 90 ]; then
        echo "✓ Disk usage: $usage%"
        return 0
    else
        echo "✗ Disk usage critical: $usage%"
        return 1
    fi
}

# Function to check memory
check_memory() {
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ $mem_usage -lt 85 ]; then
        echo "✓ Memory usage: $mem_usage%"
        return 0
    else
        echo "✗ Memory usage high: $mem_usage%"
        return 1
    fi
}

# Function to check CPU temperature
check_temperature() {
    local temp=$(vcgencmd measure_temp | sed 's/temp=//' | sed 's/°C//')
    local temp_int=${temp%.*}
    if [ $temp_int -lt 70 ]; then
        echo "✓ CPU temperature: ${temp}°C"
        return 0
    else
        echo "✗ CPU temperature high: ${temp}°C"
        return 1
    fi
}

# Run checks
errors=0

echo "=== Service Status ==="
check_service postgresql || ((errors++))
check_service nginx || ((errors++))
check_service surblend || ((errors++))
echo ""

echo "=== Port Status ==="
check_port 5432 "PostgreSQL" || ((errors++))
check_port 80 "Nginx" || ((errors++))
check_port 8000 "SurBlend API" || ((errors++))
echo ""

echo "=== System Checks ==="
check_database || ((errors++))
check_api || ((errors++))
check_disk_space || ((errors++))
check_memory || ((errors++))
check_temperature || ((errors++))
echo ""

echo "=== Recent Errors ==="
echo "Last 5 backend errors:"
sudo journalctl -u surblend -p err -n 5 --no-pager || echo "No recent errors"
echo ""

echo "=== Summary ==="
if [ $errors -eq 0 ]; then
    echo "✓ All checks passed! System is healthy."
    exit 0
else
    echo "✗ $errors check(s) failed. Please investigate."
    exit 1
fi