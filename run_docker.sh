#!/bin/bash

# Prompt for environment variables
read -p "Enter Django SECRET_KEY: " DJANGO_SECRET_KEY
read -p "Enter Django DEBUG (True/False): " DJANGO_DEBUG
read -p "Enter Django ALLOWED_HOSTS (comma separated): " DJANGO_ALLOWED_HOSTS
read -p "Enter MySQL database name: " MYSQL_DATABASE
read -p "Enter MySQL user: " MYSQL_USER
read -p "Enter MySQL password: " MYSQL_PASSWORD
read -p "Enter MySQL root password: " MYSQL_ROOT_PASSWORD

# Prompt for external MinIO config
read -p "Enter MinIO endpoint (e.g. http://159.65.8.211:9000): " MINIO_ENDPOINT
read -p "Enter MinIO access key: " MINIO_ACCESS_KEY
read -p "Enter MinIO secret key: " MINIO_SECRET_KEY
read -p "Enter MinIO bucket name: " MINIO_BUCKET_NAME

# Write .env file
cat <<EOF > .env
DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY"
DJANGO_DEBUG=$DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS
MYSQL_DATABASE=$MYSQL_DATABASE
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MINIO_ENDPOINT=$MINIO_ENDPOINT
MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY
MINIO_SECRET_KEY=$MINIO_SECRET_KEY
MINIO_BUCKET_NAME=$MINIO_BUCKET_NAME
EOF

echo ".env file created. Starting Docker Compose..."
docker compose up -d
