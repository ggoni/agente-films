#!/bin/bash

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎬 Agente Films - Multi-Agent Filmmaking System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running!"
    echo "  Please start Docker Desktop and try again."
    exit 1
fi
print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose not found!"
    echo "  Please install docker-compose and try again."
    exit 1
fi
print_success "docker-compose is available"

# Check for .env file
print_status "Checking environment configuration..."
if [ ! -f .env ]; then
    print_warning ".env file not found, creating from template..."
    cp .env.example .env
    print_success "Created .env file"
    echo ""
    print_warning "IMPORTANT: Please edit .env with your credentials:"
    echo "  - GOOGLE_CLOUD_PROJECT (required for Gemini models)"
    echo "  - OPENAI_API_KEY (optional, for GPT models)"
    echo "  - ANTHROPIC_API_KEY (optional, for Claude models)"
    echo ""
    read -p "Press Enter after editing .env, or Ctrl+C to exit..."
else
    print_success ".env file exists"
fi

# Check if GOOGLE_CLOUD_PROJECT is set
if ! grep -q "^GOOGLE_CLOUD_PROJECT=.\+" .env; then
    print_warning "GOOGLE_CLOUD_PROJECT not set in .env"
    echo "  Gemini models won't work without this."
    echo "  You can still use OpenAI or Anthropic models if configured."
fi

# Stop any running services
print_status "Stopping any existing services..."
docker-compose down > /dev/null 2>&1 || true
print_success "Cleaned up existing services"

# Build images
print_status "Building Docker images..."
docker-compose build --quiet
print_success "Images built successfully"

# Start services
print_status "Starting all services..."
echo "  - PostgreSQL (database)"
echo "  - LiteLLM Proxy (multi-model interface)"
echo "  - FastAPI Backend (API server)"
echo "  - React Frontend (web interface)"
echo ""

docker-compose up -d

print_success "All services started"

# Wait for services to be ready
print_status "Waiting for services to be ready..."
echo ""

# Wait for PostgreSQL
echo -n "  PostgreSQL "
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e " ${RED}✗${NC}"
        print_error "PostgreSQL failed to start"
        exit 1
    fi
done

# Wait for LiteLLM
echo -n "  LiteLLM Proxy "
for i in {1..30}; do
    if curl -s http://localhost:4000/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e " ${YELLOW}⚠${NC} (may need more time)"
        break
    fi
done

# Wait for API
echo -n "  FastAPI Backend "
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e " ${YELLOW}⚠${NC} (may need more time)"
        break
    fi
done

# Wait for Frontend (takes longer - npm install + dev server)
echo -n "  React Frontend (installing deps) "
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
    if [ $i -eq 60 ]; then
        echo -e " ${YELLOW}⚠${NC} (still starting, check logs with: make logs-frontend)"
        break
    fi
done

echo ""
print_success "All services are ready!"
echo ""

# Show service URLs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📍 Service URLs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  ${GREEN}Frontend:${NC}        http://localhost:3000"
echo -e "  ${GREEN}API Docs:${NC}        http://localhost:8000/docs"
echo -e "  ${GREEN}API Health:${NC}      http://localhost:8000/health"
echo -e "  ${GREEN}LiteLLM UI:${NC}      http://localhost:4000/ui"
echo -e "  ${GREEN}LiteLLM Health:${NC}  http://localhost:4000/health"
echo ""

# Show current model
CURRENT_MODEL=$(grep "^MODEL=" .env | cut -d'=' -f2)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 Current Model Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  Default Model: ${GREEN}${CURRENT_MODEL}${NC}"
echo ""
echo "  Available models:"
echo "    • gemini-2.5-flash, gemini-2.0-flash, gemini-pro"
echo "    • gpt-4, gpt-4-turbo, gpt-3.5-turbo"
echo "    • claude-3-5-sonnet, claude-3-opus, claude-3-haiku"
echo ""
echo "  Switch models:"
echo "    make switch-model MODEL=gpt-4"
echo ""

# Show useful commands
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛠  Useful Commands"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  make logs              # View all logs"
echo "  make logs-api          # View API logs"
echo "  make logs-litellm      # View LiteLLM logs"
echo "  make health            # Check service health"
echo "  make test-models       # Test all configured models"
echo "  make down              # Stop all services"
echo "  ./stop.sh              # Stop all services (alternative)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✓ Agente Films is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
