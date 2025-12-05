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

## Step 5: Set Up HPA (Optional but Recommended)

```bash
# Install metrics server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create HPA for Accounts
kubectl autoscale deployment accounts -n martianbank \
  --cpu-percent=70 \
  --min=1 \
  --max=5

# Create HPA for Transactions
kubectl autoscale deployment transactions -n martianbank \
  --cpu-percent=70 \
  --min=1 \
  --max=5

# Verify HPA
kubectl get hpa -n martianbank
```

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

