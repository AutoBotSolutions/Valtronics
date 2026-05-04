#!/bin/bash

# Valtronics Local Development Startup Script
# This script starts the Valtronics system locally without Docker

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

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_warning "PostgreSQL is not installed. You'll need to install it separately."
        log_info "Install with: sudo apt install postgresql postgresql-contrib"
    fi
    
    # Check Redis
    if ! command -v redis-server &> /dev/null; then
        log_warning "Redis is not installed. You'll need to install it separately."
        log_info "Install with: sudo apt install redis-server"
    fi
    
    log_success "Dependencies check completed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Copy .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        log_info "Created .env file from template"
    fi
    
    # Create logs directory
    mkdir -p logs
    log_info "Created logs directory"
}

# Start PostgreSQL
start_postgresql() {
    log_info "Starting PostgreSQL..."
    
    # Check if PostgreSQL is running
    if ! pg_isready -q; then
        sudo systemctl start postgresql
        log_info "PostgreSQL started"
    else
        log_info "PostgreSQL is already running"
    fi
    
    # Create database if it doesn't exist
    if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw valtronics_db; then
        log_info "Creating database..."
        sudo -u postgres createdb valtronics_db
        sudo -u postgres createuser valtronics
        sudo -u postgres psql -c "ALTER USER valtronics PASSWORD 'password';"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE valtronics_db TO valtronics;"
        log_success "Database created"
    else
        log_info "Database already exists"
    fi
}

# Start Redis
start_redis() {
    log_info "Starting Redis..."
    
    if ! pgrep -x "redis-server" > /dev/null; then
        sudo systemctl start redis-server
        log_info "Redis started"
    else
        log_info "Redis is already running"
    fi
}

# Setup backend
setup_backend() {
    log_info "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Created Python virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    log_info "Backend dependencies installed"
    
    # Run database initialization
    log_info "Initializing database..."
    psql -h localhost -U valtronics -d valtronics_db -f ../scripts/init-db.sql
    
    cd ..
}

# Setup frontend
setup_frontend() {
    log_info "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    log_info "Frontend dependencies installed"
    
    cd ..
}

# Start services
start_services() {
    log_info "Starting Valtronics services..."
    
    # Start backend
    log_info "Starting backend..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Start frontend
    log_info "Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    log_success "Services started!"
    log_info "Backend: http://localhost:8000"
    log_info "Frontend: http://localhost:3000"
    log_info "API Docs: http://localhost:8000/docs"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    # Stop backend
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_info "Backend stopped"
        fi
        rm .backend.pid
    fi
    
    # Stop frontend
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_info "Frontend stopped"
        fi
        rm .frontend.pid
    fi
    
    log_success "All services stopped"
}

# Show status
show_status() {
    log_info "Checking service status..."
    
    # Check backend
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            log_success "Backend is running (PID: $BACKEND_PID)"
        else
            log_error "Backend is not running"
        fi
    else
        log_warning "Backend PID file not found"
    fi
    
    # Check frontend
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            log_success "Frontend is running (PID: $FRONTEND_PID)"
        else
            log_error "Frontend is not running"
        fi
    else
        log_warning "Frontend PID file not found"
    fi
    
    # Check PostgreSQL
    if pg_isready -q; then
        log_success "PostgreSQL is running"
    else
        log_error "PostgreSQL is not running"
    fi
    
    # Check Redis
    if pgrep -x "redis-server" > /dev/null; then
        log_success "Redis is running"
    else
        log_error "Redis is not running"
    fi
}

# Show logs
show_logs() {
    log_info "Showing logs..."
    
    if [ "$1" = "backend" ]; then
        tail -f logs/valtronics.log 2>/dev/null || echo "No backend logs found"
    elif [ "$1" = "frontend" ]; then
        echo "Frontend logs are displayed in the terminal where npm start is running"
    else
        echo "Available logs: backend, frontend"
        echo "Usage: $0 logs [service]"
    fi
}

# Show help
show_help() {
    echo "Valtronics Local Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup       Set up the development environment"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs [service] Show logs (backend, frontend)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Initial setup"
    echo "  $0 start    # Start services"
    echo "  $0 status   # Check status"
}

# Main script logic
case "${1:-}" in
    "setup")
        check_dependencies
        setup_environment
        start_postgresql
        start_redis
        setup_backend
        setup_frontend
        log_success "Setup completed! Run '$0 start' to start services."
        ;;
    "start")
        check_dependencies
        start_postgresql
        start_redis
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        start_services
        ;;
    "status")
        show_status
        ;;
    "logs")
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
