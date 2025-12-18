# Quick Start Guide - GCP Deployment

## Overview

This is a quick reference guide for deploying Martian Bank to GCP. For detailed information, see [GCP_DEPLOYMENT_ROADMAP.md](./GCP_DEPLOYMENT_ROADMAP.md).

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│              Global HTTP(S) Load Balancer                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    GKE Cluster                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   UI     │  │ Accounts │  │Transactions│           │
│  └──────────┘  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐                          │
│  │Customer- │  │Dashboard │                          │
│  │  Auth    │  └──────────┘                          │
│  └──────────┘                                         │
│         │                                              │
│         ▼                                              │
│  ┌──────────┐                                         │
│  │  HPA     │  (Auto-scaling)                        │
│  └──────────┘                                         │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Compute Engine VM    │
         │    MongoDB Database   │
         └───────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Google Cloud Functions                     │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │ Loan Service │  │ ATM Locator  │                   │
│  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites Checklist

- [ ] GCP account with $300 free trial credits
- [ ] `gcloud` CLI installed and authenticated
- [ ] `kubectl` installed
- [ ] `helm` installed
- [ ] `docker` installed
- [ ] Basic knowledge of Kubernetes, GCP, and microservices

## Quick Deployment Steps

### 1. GCP Setup (15 minutes)
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. MongoDB VM Setup (30 minutes)
```bash
# Create VM
gcloud compute instances create mongodb-vm \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=40GB

# SSH into VM and install MongoDB
gcloud compute ssh mongodb-vm --zone=us-central1-a
# Then follow MongoDB installation steps
```

### 3. GKE Cluster Setup (20 minutes)
```bash
# Create cluster
gcloud container clusters create martianbank-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-medium

# Get credentials
gcloud container clusters get-credentials martianbank-cluster --zone=us-central1-a
```

### 4. Build and Push Images (30 minutes)
```bash
# Set project ID
export PROJECT_ID=YOUR_PROJECT_ID

# Build and push each service
docker build -t gcr.io/$PROJECT_ID/martianbank-ui:latest ./ui
docker push gcr.io/$PROJECT_ID/martianbank-ui:latest

# Repeat for: customer-auth, accounts, transactions, dashboard
```

### 5. Deploy Cloud Functions (1 hour)
```bash
# Deploy Loan Function
cd cloud-functions/loan
gcloud functions deploy loan-service \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated

# Deploy ATM Locator Function
cd ../atm-locator
gcloud functions deploy atm-locator-service \
  --runtime nodejs18 \
  --trigger-http \
  --allow-unauthenticated
```

### 6. Deploy to GKE (30 minutes)
```bash
# Update values.yaml with:
# - DB_URL (MongoDB VM IP)
# - Cloud Function URLs
# - Image repositories

# Deploy with Helm
helm install martianbank ./martianbank \
  --set DB_URL="mongodb://root:password@VM_IP:27017"
```

### 7. Configure Load Balancer (15 minutes)
```bash
# Get external IP
kubectl get service nginx -n martianbank

# Access application at http://EXTERNAL_IP:8080
```

### 8. Configure HPA (Horizontal Pod Autoscaler) - Manual Configuration (10 minutes)

**Important:** HPAs are configured manually using `kubectl` commands, not via Helm charts. This allows for fine-grained control over scaling behavior.

#### 8.1 Ensure Metrics Server is Running
```bash
# Check if metrics server exists
kubectl get deployment metrics-server -n kube-system

# If not exists, install it (required for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### 8.2 Configure HPA for Transactions Service
```bash
# Create HPA for transactions (min: 1, max: 3, CPU target: 50%)
kubectl autoscale deployment transactions -n martianbank \
  --min=1 \
  --max=3 \
  --cpu=50%

# Verify HPA creation
kubectl get hpa transactions -n martianbank
```

#### 8.3 Configure HPA for Customer-Auth Service
```bash
# Create HPA for customer-auth (fixed at 2 replicas, CPU target: 50%)
kubectl autoscale deployment customer-auth -n martianbank \
  --min=2 \
  --max=2 \
  --cpu=50%

# Verify HPA creation
kubectl get hpa customer-auth -n martianbank
```

#### 8.4 Update Existing HPA (if needed)
If HPAs already exist and you need to modify them:
```bash
# Update transactions HPA max replicas
kubectl patch hpa transactions -n martianbank -p '{"spec":{"maxReplicas":3}}'

# Update transactions HPA min replicas
kubectl patch hpa transactions -n martianbank -p '{"spec":{"minReplicas":1}}'

# Update CPU threshold (use percentage format)
kubectl patch hpa transactions -n martianbank -p '{"spec":{"metrics":[{"type":"Resource","resource":{"name":"cpu","target":{"type":"Utilization","averageUtilization":50}}}]}}'

# Update customer-auth HPA (min and max to 2)
kubectl patch hpa customer-auth -n martianbank -p '{"spec":{"minReplicas":2,"maxReplicas":2}}'
```

#### 8.5 Verify All HPAs
```bash
# List all HPAs
kubectl get hpa -n martianbank

# View detailed HPA status
kubectl describe hpa transactions -n martianbank
kubectl describe hpa customer-auth -n martianbank
```

**Note:** Other services (UI, Dashboard, Accounts, NGINX) run without HPA at fixed replica counts (1 replica each).

## Key Configuration Files

### ConfigMap (martianbank/templates/configmap.yaml)
```yaml
data:
  DB_URL: "mongodb://root:password@VM_IP:27017"
  LOAN_FUNCTION_URL: "https://REGION-PROJECT.cloudfunctions.net/loan-service"
  ATM_FUNCTION_URL: "https://REGION-PROJECT.cloudfunctions.net/atm-locator-service"
  JWT_SECRET: "your-secret-key"
```

## Cost Monitoring

### Expected Monthly Costs
- GKE Nodes (3x e2-medium): ~$139.20
- MongoDB VM (e2-small): ~$11.10
- Load Balancer: ~$18.25
- Storage: ~$4.00
- **Total: ~$172.55/month**

### Set Billing Alerts
```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Martian Bank Budget" \
  --budget-amount=300USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

## Performance Testing

### Update Locust URLs
Edit `performance_locust/api_urls.py`:
```python
ApiUrls = {
    'VITE_ACCOUNTS_URL': 'http://LOAD_BALANCER_IP/account',
    'VITE_LOAN_URL': 'https://REGION-PROJECT.cloudfunctions.net/loan-service',
    'VITE_ATM_URL': 'https://REGION-PROJECT.cloudfunctions.net/atm-locator-service',
    # ... etc
}
```

### Run Locust Tests
```bash
cd performance_locust
locust -f loan_locust.py --host=http://LOAD_BALANCER_IP
```

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl get pods -n martianbank

# Check logs
kubectl logs <pod-name> -n martianbank

# Describe pod for events
kubectl describe pod <pod-name> -n martianbank
```

### Database Connection Issues
```bash
# Test MongoDB connectivity from GKE pod
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup MONGODB_VM_IP

# Check firewall rules
gcloud compute firewall-rules list
```

### Cloud Function Not Working
```bash
# Check function logs
gcloud functions logs read loan-service --limit 50

# Test function
curl https://REGION-PROJECT.cloudfunctions.net/loan-service
```

## Useful Commands

### GKE Management
```bash
# Scale cluster
gcloud container clusters resize martianbank-cluster \
  --num-nodes=2 --zone=us-central1-a

# Get cluster info
gcloud container clusters describe martianbank-cluster --zone=us-central1-a
```

### Cost Control
```bash
# Stop VM when not in use
gcloud compute instances stop mongodb-vm --zone=us-central1-a

# Start VM
gcloud compute instances start mongodb-vm --zone=us-central1-a

# Delete cluster (when done)
gcloud container clusters delete martianbank-cluster --zone=us-central1-a
```

## Next Steps

1. Read the full [GCP_DEPLOYMENT_ROADMAP.md](./GCP_DEPLOYMENT_ROADMAP.md)
2. Set up GCP project and enable APIs
3. Follow Phase 1 of the roadmap
4. Proceed systematically through each phase

## Support Resources

- [GCP Documentation](https://cloud.google.com/docs)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Remember**: Always monitor costs and stop resources when not actively testing!

                  


db.createUser({
  user: "root",
  pwd: "123456789",  
  roles: [ { role: "root", db: "admin" } ]
})

db.createUser({
  user: "bankuser",
  pwd: "123456789",
  roles: [ { role: "readWrite", db: "bank" } ]
})