#!/bin/bash

# Valtronics Deployment Script
# This script handles deployment of the Valtronics system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="valtronics"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
DOCKER_REGISTRY="your-registry.com"
VERSION=${1:-"latest"}

# Functions
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

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_warning "kubectl is not installed (optional for Kubernetes deployment)"
    fi
    
    log_success "Dependencies check completed"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    cd $BACKEND_DIR
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}/backend:${VERSION} .
    docker tag ${DOCKER_REGISTRY}/${PROJECT_NAME}/backend:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}/backend:latest
    cd ..
    
    # Build frontend image
    log_info "Building frontend image..."
    cd $FRONTEND_DIR
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}/frontend:${VERSION} .
    docker tag ${DOCKER_REGISTRY}/${PROJECT_NAME}/frontend:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}/frontend:latest
    cd ..
    
    log_success "Docker images built successfully"
}

push_images() {
    log_info "Pushing Docker images to registry..."
    
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}/backend:${VERSION}
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}/backend:latest
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}/frontend:${VERSION}
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}/frontend:latest
    
    log_success "Images pushed successfully"
}

deploy_local() {
    log_info "Deploying to local Docker Compose..."
    
    # Stop existing services
    docker-compose down || true
    
    # Build and start services
    docker-compose up -d --build
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    if curl -f http://localhost:8000/api/v1/health/ping > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend health check failed"
    fi
    
    log_success "Local deployment completed"
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is required for Kubernetes deployment"
        exit 1
    fi
    
    # Apply secrets
    log_info "Applying secrets..."
    kubectl apply -f cloud/kubernetes/secrets.yaml
    
    # Deploy database
    log_info "Deploying database..."
    kubectl apply -f cloud/kubernetes/postgres-deployment.yaml
    
    # Wait for database to be ready
    kubectl wait --for=condition=ready pod -l app=valtronics-postgres --timeout=300s
    
    # Deploy Redis
    log_info "Deploying Redis..."
    kubectl apply -f cloud/kubernetes/redis-deployment.yaml
    
    # Deploy MQTT
    log_info "Deploying MQTT broker..."
    kubectl apply -f cloud/kubernetes/mqtt-deployment.yaml
    
    # Deploy backend
    log_info "Deploying backend..."
    kubectl apply -f cloud/kubernetes/backend-deployment.yaml
    
    # Wait for backend to be ready
    kubectl wait --for=condition=available deployment valtronics-backend --timeout=300s
    
    # Deploy frontend
    log_info "Deploying frontend..."
    kubectl apply -f cloud/kubernetes/frontend-deployment.yaml
    
    # Wait for frontend to be ready
    kubectl wait --for=condition=available deployment valtronics-frontend --timeout=300s
    
    log_success "Kubernetes deployment completed"
}

run_tests() {
    log_info "Running tests..."
    
    # Backend tests
    log_info "Running backend tests..."
    cd $BACKEND_DIR
    python -m pytest tests/ -v || true
    cd ..
    
    # Frontend tests
    log_info "Running frontend tests..."
    cd $FRONTEND_DIR
    npm test -- --coverage --watchAll=false || true
    cd ..
    
    log_success "Tests completed"
}

setup_database() {
    log_info "Setting up database..."
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    until docker-compose exec postgres pg_isready -U valtronics; do
        sleep 2
    done
    
    # Run initialization script
    log_info "Running database initialization..."
    docker-compose exec -T postgres psql -U valtronics -d valtronics_db < scripts/init-db.sql
    
    log_success "Database setup completed"
}

cleanup() {
    log_info "Cleaning up..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove unused volumes (with confirmation)
    read -p "Remove unused Docker volumes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
    fi
    
    log_success "Cleanup completed"
}

show_logs() {
    log_info "Showing logs..."
    
    if [ "$1" = "backend" ]; then
        docker-compose logs -f backend
    elif [ "$1" = "frontend" ]; then
        docker-compose logs -f frontend
    elif [ "$1" = "postgres" ]; then
        docker-compose logs -f postgres
    elif [ "$1" = "redis" ]; then
        docker-compose logs -f redis
    elif [ "$1" = "mqtt" ]; then
        docker-compose logs -f mosquitto
    else
        docker-compose logs -f
    fi
}

show_help() {
    echo "Valtronics Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build              Build Docker images"
    echo "  push               Push images to registry"
    echo "  deploy-local       Deploy to local Docker Compose"
    echo "  deploy-k8s         Deploy to Kubernetes"
    echo "  test               Run tests"
    echo "  setup-db           Initialize database"
    echo "  cleanup            Clean up Docker resources"
    echo "  logs [service]     Show logs (backend, frontend, postgres, redis, mqtt)"
    echo "  help               Show this help message"
    echo ""
    echo "Options:"
    echo "  VERSION            Image version (default: latest)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy-local"
    echo "  $0 deploy-k8s"
    echo "  $0 build 1.0.0"
    echo "  $0 logs backend"
}

# Main script logic
case "${1:-}" in
    "build")
        check_dependencies
        build_images
        ;;
    "push")
        check_dependencies
        push_images
        ;;
    "deploy-local")
        check_dependencies
        deploy_local
        ;;
    "deploy-k8s")
        check_dependencies
        deploy_kubernetes
        ;;
    "test")
        check_dependencies
        run_tests
        ;;
    "setup-db")
        check_dependencies
        setup_database
        ;;
    "cleanup")
        check_dependencies
        cleanup
        ;;
    "logs")
        check_dependencies
        show_logs "$2"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        show_help
        exit 1
        ;;
esac
