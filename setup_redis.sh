#!/bin/bash

sudo dnf update -y

sudo dnf install -y docker

sudo systemctl start docker
sudo systemctl enable docker

sudo docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7

echo "⏳ Esperando a que Redis arranque..."
sleep 3

echo "🔍 Probando Redis..."
sudo docker exec redis redis-cli ping

echo "✅ Redis listo!"
