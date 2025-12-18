# Deployment Steps - Martian Bank to GKE

## Prerequisites ✅
- ✅ GKE cluster created and connected
- ✅ MongoDB VM running (IP: 10.128.0.2)
- ✅ All Docker images built and pushed to GCR
- ✅ Helm templates updated with GCR images
- ✅ Namespace `martianbank` exists

## Step 1: Create ConfigMap

**You need your MongoDB root password!** Replace `YOUR_MONGODB_PASSWORD` below:

```bash
# Set variables
export MONGODB_IP="10.128.0.2"
export MONGODB_PASSWORD="YOUR_MONGODB_PASSWORD"  # Replace with your actual password
export JWT_SECRET=$(openssl rand -hex 32)

# Create ConfigMap
kubectl create configmap configmap-martianbank \
  --from-literal=DB_URL="mongodb://root:${MONGODB_PASSWORD}@${MONGODB_IP}:27017/bank?authSource=admin" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --namespace=martianbank
```

## Step 2: Deploy with Helm

```bash
export PROJECT_ID=$(gcloud config get-value project)
export MONGODB_IP="10.128.0.2"
export MONGODB_PASSWORD="YOUR_MONGODB_PASSWORD"  # Replace with your actual password

helm install martianbank ./martianbank \
  --namespace martianbank \
  --set SERVICE_PROTOCOL=http \
  --set DB_URL="mongodb://root:${MONGODB_PASSWORD}@${MONGODB_IP}:27017/bank?authSource=admin" \
  --set imageRegistry="gcr.io/$PROJECT_ID" \
  --set mongodb.enabled=false \
  --set nginx.enabled=true
```

## Step 3: Check Deployment Status

```bash
# Watch pods until all are Running
kubectl get pods -n martianbank -w

# In another terminal, check services
kubectl get services -n martianbank

# Check for external IP (may take 1-2 minutes)
kubectl get service nginx -n martianbank
```

## Step 4: Get External IP

Wait for the LoadBalancer to assign an external IP:

```bash
kubectl get service nginx -n martianbank -w
```

Once you see an EXTERNAL-IP (not `<pending>`), access your app at:
```
http://EXTERNAL_IP:8080
```

## Step 5: Set Up HPA (Manual Configuration - Required)

**Important:** HPAs are configured manually using `kubectl` commands, not via Helm charts. Only transactions and customer-auth services have HPA enabled.

```bash
# Install metrics server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Wait for metrics server to be ready
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=90s

# Create HPA for Transactions Service (min: 1, max: 3, CPU target: 50%)
kubectl autoscale deployment transactions -n martianbank \
  --min=1 \
  --max=3 \
  --cpu=50%

# Create HPA for Customer-Auth Service (fixed at 2 replicas, CPU target: 50%)
kubectl autoscale deployment customer-auth -n martianbank \
  --min=2 \
  --max=2 \
  --cpu=50%

# Verify HPAs
kubectl get hpa -n martianbank

# View detailed HPA status
kubectl describe hpa transactions -n martianbank
kubectl describe hpa customer-auth -n martianbank
```

**Note:** Other services (UI, Dashboard, Accounts, NGINX) run without HPA at fixed replica counts (1 replica each).

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl get pods -n martianbank

# Describe pod for events
kubectl describe pod <pod-name> -n martianbank

# Check logs
kubectl logs <pod-name> -n martianbank
```

### Database Connection Issues
```bash
# Test MongoDB connectivity from a pod
kubectl run -it --rm mongo-test --image=mongo:latest --restart=Never --namespace=martianbank -- mongosh "mongodb://root:PASSWORD@10.128.0.2:27017/admin?authSource=admin"
```

### Service Not Getting External IP
```bash
# Check service status
kubectl describe service nginx -n martianbank

# Check for LoadBalancer events
kubectl get events -n martianbank --sort-by='.lastTimestamp'
```

## Quick Deployment Script

Or use the automated script:

```bash
./scripts/deploy.sh YOUR_MONGODB_PASSWORD
```

This script will:
- Create ConfigMap
- Deploy with Helm
- Wait for pods
- Show external IP

---

**Ready?** Start with Step 1 above!

