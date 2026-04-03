#!/bin/bash

echo "Updating system..."
sudo dnf update -y

echo "Installing Docker..."
sudo dnf install -y docker

echo "Starting Docker..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Removing existing Redis container if exists..."
sudo docker rm -f redis 2>/dev/null

echo "Running Redis container..."
sudo docker run -d \
  --name redis \
  --restart unless-stopped \
  -p 6379:6379 \
  redis:7

echo "⏳ Waiting for Redis to start..."
sleep 3

echo "🔍 Testing Redis..."
sudo docker exec redis redis-cli ping

echo "✅ Redis is ready!"