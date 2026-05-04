#!/bin/bash

# Docker Installation Script for Ubuntu/Debian
# This script installs Docker and Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

log_info "Installing Docker and Docker Compose for Valtronics..."

# Update package index
log_info "Updating package index..."
apt update

# Install prerequisites
log_info "Installing prerequisites..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

# Add Docker's official GPG key
log_info "Adding Docker GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
log_info "Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
log_info "Installing Docker Engine..."
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
log_info "Starting Docker service..."
systemctl start docker
systemctl enable docker

# Add current user to docker group (if not root)
if [ "$SUDO_USER" ]; then
    log_info "Adding $SUDO_USER to docker group..."
    usermod -aG docker $SUDO_USER
    log_warning "You will need to log out and log back in for group changes to take effect"
fi

# Install Docker Compose (standalone)
log_info "Installing Docker Compose..."
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
log_info "Verifying Docker installation..."
docker --version
docker compose version

# Create docker group if it doesn't exist
if ! getent group docker > /dev/null 2>&1; then
    groupadd docker
fi

# Test Docker with hello-world
log_info "Testing Docker with hello-world container..."
docker run hello-world

log_success "Docker and Docker Compose installation completed!"
log_info "You can now run: cd /home/robbie/Desktop/Valtronics/valtronics && docker compose up -d"

# Instructions for non-root usage
if [ "$SUDO_USER" ]; then
    echo ""
    log_warning "IMPORTANT: If you want to run Docker without sudo:"
    echo "1. Log out and log back in (or run: newgrp docker)"
    echo "2. Then you can run docker commands without sudo"
fi
