#!/bin/bash

# Add the Debian stable main repository to the sources list
echo "deb http://ftp.debian.org/debian stable main" | tee -a /etc/apt/sources.list

# Update the package list
apt-get update

# Upgrade SQLite3
apt-get install -y sqlite3

# Install the SpaCy language model
python -m spacy download en_core_web_sm

# Start Gunicorn server with the specified settings
gunicorn --bind=0.0.0.0 --timeout 600 main:app
