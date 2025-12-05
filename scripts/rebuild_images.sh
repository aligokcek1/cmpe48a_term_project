#!/bin/bash

# Rebuild Docker images using GCP Cloud Build (builds for linux/amd64 automatically)
# Usage: ./scripts/rebuild_images.sh [service-name]
# If no service-name provided, rebuilds all images

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Could not get GCP project ID.${NC}"
    exit 1
fi

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Function to build with Cloud Build
build_image() {
    local service=$1
    local dockerfile=$2
    local context=$3
    
    echo -e "${YELLOW}Building $service...${NC}"
    
    # Create temporary cloudbuild file
    cat > /tmp/cloudbuild-$service.yaml <<EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-f', '$dockerfile', '-t', 'gcr.io/$PROJECT_ID/martianbank-$service:latest', '.']
images:
- 'gcr.io/$PROJECT_ID/martianbank-$service:latest'
EOF
    
    if [ "$context" = "." ]; then
        gcloud builds submit --config /tmp/cloudbuild-$service.yaml .
    else
        gcloud builds submit --config /tmp/cloudbuild-$service.yaml $context
    fi
    
    rm /tmp/cloudbuild-$service.yaml
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $service built${NC}"
    else
        echo -e "${RED}✗ $service failed${NC}"
        return 1
    fi
    echo ""
}

# If service name provided, build only that service
if [ -n "$1" ]; then
    SERVICE=$1
    case $SERVICE in
        ui)
            build_image "ui" "Dockerfile" "./ui"
            ;;
        customer-auth)
            build_image "customer-auth" "Dockerfile" "./customer-auth"
            ;;
        nginx)
            build_image "nginx" "Dockerfile" "./nginx"
            ;;
        accounts)
            build_image "accounts" "accounts/Dockerfile" "."
            ;;
        transactions)
            build_image "transactions" "transactions/Dockerfile" "."
            ;;
        dashboard)
            build_image "dashboard" "dashboard/Dockerfile" "."
            ;;
        atm-locator)
            build_image "atm-locator" "Dockerfile" "./atm-locator"
            ;;
        loan)
            build_image "loan" "loan/Dockerfile" "."
            ;;
        *)
            echo -e "${RED}Unknown service: $SERVICE${NC}"
            echo "Available services: ui, customer-auth, nginx, accounts, transactions, dashboard, atm-locator, loan"
            exit 1
            ;;
    esac
else
    # Build all images
    echo -e "${GREEN}Rebuilding all images using GCP Cloud Build${NC}"
    echo -e "${GREEN}Project ID: $PROJECT_ID${NC}"
    echo ""
    
    build_image "ui" "Dockerfile" "./ui"
    build_image "customer-auth" "Dockerfile" "./customer-auth"
    build_image "nginx" "Dockerfile" "./nginx"
    build_image "accounts" "accounts/Dockerfile" "."
    build_image "transactions" "transactions/Dockerfile" "."
    build_image "dashboard" "dashboard/Dockerfile" "."
    build_image "atm-locator" "Dockerfile" "./atm-locator"
    build_image "loan" "loan/Dockerfile" "."
    
    echo -e "${GREEN}All images rebuilt!${NC}"
fi

