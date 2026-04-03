#!/bin/bash

echo "Updating system..."
sudo dnf update -y

echo "Installing Python, pip and git..."
sudo dnf install -y python3 python3-pip git

echo "Installing Python dependencies..."
pip3 install flask redis gunicorn requests

echo "Copying systemd service..."
sudo cp api/api.service /etc/systemd/system/api.service

echo "Reloading systemd..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "Enabling API service..."
sudo systemctl enable api

echo "Starting API service..."
sudo systemctl start api

echo "Checking API status..."
sudo systemctl status api --no-pager