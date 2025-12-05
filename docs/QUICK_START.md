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

## Key Configuration Files

### ConfigMap (martianbank/templates/configmap.yaml)
```yaml
data:
  DB_URL: "mongodb://root:password@VM_IP:27017"
  LOAN_FUNCTION_URL: "https://REGION-PROJECT.cloudfunctions.net/loan-service"
  ATM_FUNCTION_URL: "https://REGION-PROJECT.cloudfunctions.net/atm-locator-service"
  JWT_SECRET: "your-secret-key"
```

### HPA Configuration
```yaml
# Enable in values.yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70
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