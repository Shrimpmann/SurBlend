#!/usr/bin/env python3
"""
System monitoring script for SurBlend on Raspberry Pi
Sends alerts if resources are running low
"""

import psutil
import subprocess
import logging
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
WARNING_THRESHOLDS = {
    'cpu_percent': 80,
    'memory_percent': 85,
    'disk_percent': 90,
    'temperature': 70  # Celsius
}

LOG_FILE = '/opt/surblend/logs/monitor.log'
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'jonmarsh@bullochfertilizer.com')

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_cpu_temperature():
    """Get CPU temperature on Raspberry Pi"""
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'],
            capture_output=True,
            text=True
        )
        temp_str = result.stdout.strip()
        temp = float(temp_str.split('=')[1].split("'")[0])
        return temp
    except:
        return None

def check_services():
    """Check if critical services are running"""
    services = ['postgresql', 'nginx', 'surblend']
    status = {}
    
    for service in services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True,
                text=True
            )
            status[service] = result.stdout.strip() == 'active'
        except:
            status[service] = False
    
    return status

def send_alert(subject, message):
    """Send email alert"""
    try:
        # Configure with your SMTP settings
        smtp_server = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASSWORD')
        
        if not smtp_user or not smtp_pass:
            logging.warning("SMTP credentials not configured")
            return
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = f"SurBlend Alert: {subject}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
        logging.info(f"Alert sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")

def main():
    """Main monitoring function"""
    alerts = []
    
    # Check CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > WARNING_THRESHOLDS['cpu_percent']:
        alerts.append(f"High CPU usage: {cpu_percent}%")
    
    # Check Memory
    memory = psutil.virtual_memory()
    if memory.percent > WARNING_THRESHOLDS['memory_percent']:
        alerts.append(f"High memory usage: {memory.percent}%")
    
    # Check Disk
    disk = psutil.disk_usage('/')
    if disk.percent > WARNING_THRESHOLDS['disk_percent']:
        alerts.append(f"Low disk space: {disk.percent}% used")
    
    # Check Temperature
    temp = get_cpu_temperature()
    if temp and temp > WARNING_THRESHOLDS['temperature']:
        alerts.append(f"High CPU temperature: {temp}°C")
    
    # Check Services
    services = check_services()
    for service, is_running in services.items():
        if not is_running:
            alerts.append(f"Service {service} is not running")
    
    # Log status
    logging.info(f"System check - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
    
    # Send alerts if any
    if alerts:
        alert_message = "System monitoring detected the following issues:\n\n"
        alert_message += "\n".join(f"- {alert}" for alert in alerts)
        alert_message += f"\n\nTimestamp: {datetime.now()}"
        
        send_alert("System Warning", alert_message)
        
        for alert in alerts:
            logging.warning(alert)

if __name__ == "__main__":
    main()