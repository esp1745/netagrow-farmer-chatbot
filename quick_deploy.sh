#!/bin/bash

# Quick Deployment Script for Netagrow Chatbot on AWS EC2
# Run this script on your EC2 instance after uploading your files

echo "🚀 Quick Deployment for Netagrow Chatbot"

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx supervisor

# Create app directory
sudo mkdir -p /var/www/netagrow-chatbot
sudo chown ubuntu:ubuntu /var/www/netagrow-chatbot

# Copy files (assuming you're in the project directory)
cp -r * /var/www/netagrow-chatbot/

# Setup Python environment
cd /var/www/netagrow-chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Weather API Configuration
WEATHER_API_KEY=your_weather_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_ACCESS_TOKEN=your_supabase_access_token_here

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
EOF
    echo "⚠️ Please edit .env with your actual API keys"
fi

# Configure supervisor
sudo tee /etc/supervisor/conf.d/netagrow-chatbot.conf > /dev/null << EOF
[program:netagrow-chatbot]
directory=/var/www/netagrow-chatbot
command=/var/www/netagrow-chatbot/venv/bin/gunicorn --bind 0.0.0.0:8000 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/netagrow-chatbot/err.log
stdout_logfile=/var/log/netagrow-chatbot/out.log
user=ubuntu
environment=PATH="/var/www/netagrow-chatbot/venv/bin"
EOF

# Create log directory
sudo mkdir -p /var/log/netagrow-chatbot
sudo chown ubuntu:ubuntu /var/log/netagrow-chatbot

# Configure nginx
sudo tee /etc/nginx/sites-available/netagrow-chatbot > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/netagrow-chatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start netagrow-chatbot

sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment completed!"
echo "📝 Next steps:"
echo "1. Edit /var/www/netagrow-chatbot/.env with your API keys"
echo "2. Restart: sudo supervisorctl restart netagrow-chatbot"
echo "3. Test: curl http://localhost/health" 