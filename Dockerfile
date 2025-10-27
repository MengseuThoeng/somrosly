# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && \
	apt-get install -y pkg-config default-libmysqlclient-dev build-essential && \
	rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "Somrosly.wsgi:application", "--bind", "0.0.0.0:8000"]
