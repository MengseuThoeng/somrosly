#!/bin/bash

# Prompt for environment variables
read -p "Enter Django SECRET_KEY: " DJANGO_SECRET_KEY
read -p "Enter Django DEBUG (True/False): " DJANGO_DEBUG
read -p "Enter Django ALLOWED_HOSTS (comma separated): " DJANGO_ALLOWED_HOSTS
read -p "Enter MySQL database name: " MYSQL_DATABASE
read -p "Enter MySQL user: " MYSQL_USER
read -p "Enter MySQL password: " MYSQL_PASSWORD
read -p "Enter MySQL root password: " MYSQL_ROOT_PASSWORD
read -p "Enter MinIO root user: " MINIO_ROOT_USER
read -p "Enter MinIO root password: " MINIO_ROOT_PASSWORD

# Write .env file
cat <<EOF > .env
DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY"
DJANGO_DEBUG=$DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS
MYSQL_DATABASE=$MYSQL_DATABASE
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MINIO_ROOT_USER=$MINIO_ROOT_USER
MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD
EOF

echo ".env file created. Starting Docker Compose..."
docker compose up -d
