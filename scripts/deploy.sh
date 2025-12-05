#!/bin/bash

# Deploy Martian Bank to GKE
# Usage: ./scripts/deploy.sh [MONGODB_PASSWORD]

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

# Get MongoDB VM IP
MONGODB_IP=$(gcloud compute instances describe mongodb-vm --zone=us-central1-a --format='get(networkInterfaces[0].networkIP)' 2>/dev/null)

if [ -z "$MONGODB_IP" ]; then
    echo -e "${RED}Error: Could not find MongoDB VM.${NC}"
    echo "Make sure your VM is named 'mongodb-vm' or update the script."
    exit 1
fi

echo -e "${GREEN}Deploying Martian Bank to GKE${NC}"
echo -e "${GREEN}Project ID: $PROJECT_ID${NC}"
echo -e "${GREEN}MongoDB IP: $MONGODB_IP${NC}"
echo ""

# Get MongoDB password
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter MongoDB root password:${NC}"
    read -s MONGODB_PASSWORD
    echo ""
else
    MONGODB_PASSWORD=$1
fi

if [ -z "$MONGODB_PASSWORD" ]; then
    echo -e "${RED}Error: MongoDB password is required${NC}"
    exit 1
fi

# Generate JWT secret if not provided
JWT_SECRET="${2:-$(openssl rand -hex 32)}"

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Check if namespace exists
if ! kubectl get namespace martianbank &>/dev/null; then
    echo -e "${YELLOW}Creating namespace...${NC}"
    kubectl create namespace martianbank
fi

# Prepare deployment values
DB_URL="mongodb://root:${MONGODB_PASSWORD}@${MONGODB_IP}:27017/bank?authSource=admin"

echo -e "${GREEN}ConfigMap will be created by Helm${NC}"
echo ""

# Deploy with Helm (Helm will create the ConfigMap)
echo -e "${YELLOW}Deploying with Helm...${NC}"
helm upgrade --install martianbank ./martianbank \
  --namespace martianbank \
  --set SERVICE_PROTOCOL=http \
  --set DB_URL="$DB_URL" \
  --set JWT_SECRET="$JWT_SECRET" \
  --set imageRegistry="gcr.io/$PROJECT_ID" \
  --set mongodb.enabled=false \
  --set nginx.enabled=true \
  --wait --timeout 10m

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment successful!${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi

# Wait for LoadBalancer IP
echo ""
echo -e "${YELLOW}Waiting for LoadBalancer IP assignment...${NC}"
kubectl wait --for=condition=ready pod -l app=nginx -n martianbank --timeout=300s 2>/dev/null || true

# Get external IP
EXTERNAL_IP=$(kubectl get service nginx -n martianbank -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

if [ -z "$EXTERNAL_IP" ]; then
    echo -e "${YELLOW}External IP not yet assigned. Checking status...${NC}"
    kubectl get service nginx -n martianbank
    echo ""
    echo -e "${YELLOW}Run this command to check for IP:${NC}"
    echo "  kubectl get service nginx -n martianbank"
else
    echo -e "${GREEN}✓ External IP assigned: $EXTERNAL_IP${NC}"
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}Application URL: http://$EXTERNAL_IP:8080${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
fi

# Show pod status
echo ""
echo -e "${YELLOW}Pod Status:${NC}"
kubectl get pods -n martianbank

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n martianbank"
echo "  kubectl get services -n martianbank"
echo "  kubectl logs <pod-name> -n martianbank"
echo "  kubectl get hpa -n martianbank"
echo "  kubectl describe pod <pod-name> -n martianbank"

