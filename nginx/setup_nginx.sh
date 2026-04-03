#!/bin/bash

echo "Installing NGINX..."
sudo dnf install -y nginx

echo "Stopping NGINX..."
sudo systemctl stop nginx

echo "Copying configuration..."
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf

echo "Testing configuration..."
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "NGINX config test failed ❌"
    exit 1
fi

echo "Starting NGINX..."
sudo systemctl start nginx

echo "Enabling NGINX..."
sudo systemctl enable nginx

echo "NGINX setup complete ✅"