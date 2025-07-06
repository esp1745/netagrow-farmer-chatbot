# AWS EC2 Deployment Guide for Zambian Farmer Chatbot

## Prerequisites
- AWS Account
- EC2 Instance (Ubuntu 22.04 LTS recommended)
- Domain name (optional but recommended)
- SSL certificate (for production)

## Step 1: Launch EC2 Instance

### Instance Configuration
- **AMI**: Ubuntu 22.04 LTS (ami-0c7217cdde317cfec for us-east-1)
- **Instance Type**: t2.micro (free tier) or t3.small for better performance
- **Storage**: 8GB minimum (20GB recommended)
- **Security Group**: Create new with these rules:
  - SSH (Port 22) - Your IP
  - HTTP (Port 80) - 0.0.0.0/0
  - HTTPS (Port 443) - 0.0.0.0/0
  - Custom TCP (Port 8000) - 0.0.0.0/0 (for development)

## Step 2: Connect to EC2 Instance

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

## Step 3: Install Dependencies

```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install nginx supervisor -y

# Install PostgreSQL (if needed locally)
sudo apt install postgresql postgresql-contrib -y
```

## Step 4: Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/netagrow-chatbot
sudo chown ubuntu:ubuntu /var/www/netagrow-chatbot

# Clone your repository (if using Git)
cd /var/www/netagrow-chatbot
git clone https://github.com/your-username/netagrow-chatbot.git .

# Or upload files manually via SCP
scp -i your-key.pem -r /path/to/local/project/* ubuntu@your-ec2-public-ip:/var/www/netagrow-chatbot/
```

## Step 5: Setup Python Environment

```bash
cd /var/www/netagrow-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

### Environment Variables (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Weather API Configuration
WEATHER_API_KEY=your_weather_api_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_ACCESS_TOKEN=your_supabase_access_token

# Database Configuration (if using local PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

## Step 6: Configure Gunicorn

```bash
# Test gunicorn
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 app:app
```

## Step 7: Setup Supervisor

```bash
# Create supervisor configuration
sudo nano /etc/supervisor/conf.d/netagrow-chatbot.conf
```

### Supervisor Configuration
```ini
[program:netagrow-chatbot]
directory=/var/www/netagrow-chatbot
command=/var/www/netagrow-chatbot/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/netagrow-chatbot/err.log
stdout_logfile=/var/log/netagrow-chatbot/out.log
user=ubuntu
environment=PATH="/var/www/netagrow-chatbot/venv/bin"
```

```bash
# Create log directory
sudo mkdir -p /var/log/netagrow-chatbot
sudo chown ubuntu:ubuntu /var/log/netagrow-chatbot

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start netagrow-chatbot
```

## Step 8: Configure Nginx (Optional but Recommended)

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/netagrow-chatbot
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/netagrow-chatbot/static/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/netagrow-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 9: Setup SSL with Let's Encrypt (Optional)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Step 10: Security Hardening

```bash
# Configure firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Set up automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Step 11: Monitoring and Logs

```bash
# Check application status
sudo supervisorctl status netagrow-chatbot

# View logs
tail -f /var/log/netagrow-chatbot/out.log
tail -f /var/log/netagrow-chatbot/err.log

# Check nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Step 12: Environment-Specific Configuration

### Development vs Production
- Update `app.py` to use production settings
- Set `debug=False` in production
- Use environment variables for all sensitive data
- Configure proper logging

### Database Configuration
- If using Supabase (recommended): No local database needed
- If using local PostgreSQL: Configure connection pooling

## Troubleshooting

### Common Issues
1. **Port 8000 not accessible**: Check security group rules
2. **Application not starting**: Check supervisor logs
3. **Environment variables not loading**: Ensure .env file exists and is readable
4. **Static files not serving**: Check nginx configuration

### Useful Commands
```bash
# Restart application
sudo supervisorctl restart netagrow-chatbot

# Check application logs
sudo supervisorctl tail netagrow-chatbot

# Restart nginx
sudo systemctl restart nginx

# Check system resources
htop
df -h
free -h
```

## Cost Optimization

### Free Tier Usage
- Use t2.micro instance (free for 12 months)
- Use Amazon S3 for static file storage
- Use CloudFront for CDN (free tier available)

### Scaling Considerations
- Use Application Load Balancer for multiple instances
- Use RDS for database (if needed)
- Use ElastiCache for Redis (if needed)

## Backup Strategy

```bash
# Create backup script
nano /var/www/netagrow-chatbot/backup.sh
```

```bash
#!/bin/bash
# Backup application files
tar -czf /backup/netagrow-chatbot-$(date +%Y%m%d).tar.gz /var/www/netagrow-chatbot

# Backup database (if using local PostgreSQL)
pg_dump database_name > /backup/database-$(date +%Y%m%d).sql

# Keep only last 7 days of backups
find /backup -name "*.tar.gz" -mtime +7 -delete
find /backup -name "*.sql" -mtime +7 -delete
```

## Deployment Checklist

- [ ] EC2 instance launched and configured
- [ ] Security groups configured
- [ ] Application files uploaded
- [ ] Python environment setup
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Gunicorn tested
- [ ] Supervisor configured
- [ ] Nginx configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Application tested and working

## Next Steps

1. Set up monitoring with CloudWatch
2. Configure automatic deployments with GitHub Actions
3. Set up domain and DNS
4. Implement CI/CD pipeline
5. Add health checks and monitoring
6. Set up alerts for downtime 