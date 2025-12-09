# Martian Bank - Project Status & Development Guide

**Last Updated:** December 8, 2025  
**Project:** CMPE 48A Term Project - Martian Bank GCP Deployment  
**Status:** Phase 3 Complete (Cloud Functions) - Ready for Performance Testing  
**Completion:** ~70%

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Project Overview](#project-overview)
3. [Infrastructure & IPs](#infrastructure--ips)
4. [Current Deployment Status](#current-deployment-status)
5. [Architecture](#architecture)
6. [Access Points & URLs](#access-points--urls)
7. [Development Workflow](#development-workflow)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## 🚀 Quick Reference

### Application Access
- **Main Application URL:** http://136.119.54.74:8080
- **GCP Project:** `cmpe48a-term-project`
- **GKE Cluster:** `martianbank-cluster` (us-central1-a)
- **Namespace:** `martianbank`

### Key IPs & Endpoints
- **Load Balancer IP:** `136.119.54.74:8080`
- **MongoDB VM IP:** `10.128.0.2:27017`
- **GKE Master IP:** `34.9.197.138`

### Cloud Functions
- **Loan Request:** https://loan-request-gcb4q3froa-uc.a.run.app
- **Loan History:** https://loan-history-gcb4q3froa-uc.a.run.app
- **ATM Locator:** https://atm-locator-service-gcb4q3froa-uc.a.run.app

---

## 📊 Project Overview

### What is This Project?

Martian Bank is a cloud-native microservices banking application deployed on Google Cloud Platform. It demonstrates:
- **Containerized workloads** on Google Kubernetes Engine (GKE)
- **Virtual Machines** for database (MongoDB on Compute Engine)
- **Serverless functions** (Cloud Functions for Loan & ATM services)
- **Auto-scaling** with Horizontal Pod Autoscaler (HPA)
- **Load balancing** via GCP Load Balancer

### Current Status

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: GKE Setup | ✅ Complete | 100% |
| Phase 2: MongoDB VM | ✅ Complete | 100% |
| Phase 3: Cloud Functions | ✅ Complete | 100% |
| Phase 4: Application Deployment | ✅ Complete | 100% |
| Phase 5: HPA & Load Balancer | ✅ Complete | 100% |
| Phase 6: Performance Testing | ⏳ Pending | 0% |
| Phase 7: Cost Monitoring | ⏳ Pending | 0% |
| Phase 8: Documentation | ⏳ In Progress | 50% |
| Phase 9: Final Testing | ⏳ Pending | 0% |
| Phase 10: Demo Video | ⏳ Pending | 0% |

**Overall Progress:** ~70% Complete

---

## 🏗️ Infrastructure & IPs

### GCP Project Details

```
Project ID: cmpe48a-term-project
Region: us-central1
Zone: us-central1-a
```

### Google Kubernetes Engine (GKE)

```
Cluster Name: martianbank-cluster
Location: us-central1-a
Status: RUNNING
Master IP: 34.9.197.138
Node Pool: default-pool
  - 3 nodes (e2-medium: 2 vCPU, 4GB RAM each)
  - Auto-scaling: 2-5 nodes
  - Auto-repair: Enabled
  - Auto-upgrade: Enabled
```

**Connect to Cluster:**
```bash
gcloud container clusters get-credentials martianbank-cluster \
  --zone=us-central1-a \
  --project=cmpe48a-term-project
```

### Compute Engine - MongoDB VM

```
Instance Name: mongodb-vm
Zone: us-central1-a
Status: RUNNING
Internal IP: 10.128.0.2
External IP: (None - internal only)
Machine Type: e2-small (0.5 vCPU, 2GB RAM)
OS: Ubuntu 22.04 LTS
MongoDB Port: 27017
```

**MongoDB Connection:**
```
mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin
```

**SSH to VM:**
```bash
gcloud compute ssh mongodb-vm --zone=us-central1-a
```

### Load Balancer

```
Service: nginx (LoadBalancer type)
External IP: 136.119.54.74
Port: 8080
Protocol: HTTP
Status: Active
```

**Application URL:** http://136.119.54.74:8080

### Container Registry

```
Registry: gcr.io/cmpe48a-term-project
Images:
  - gcr.io/cmpe48a-term-project/martianbank-ui:latest
  - gcr.io/cmpe48a-term-project/martianbank-customer-auth:latest
  - gcr.io/cmpe48a-term-project/martianbank-accounts:latest
  - gcr.io/cmpe48a-term-project/martianbank-transactions:latest
  - gcr.io/cmpe48a-term-project/martianbank-dashboard:latest
  - gcr.io/cmpe48a-term-project/martianbank-nginx:latest
```

---

## 📦 Current Deployment Status

### Kubernetes Services

| Service | Type | Cluster IP | External IP | Port | Status |
|---------|------|-----------|--------------|------|--------|
| **nginx** | LoadBalancer | 34.118.231.229 | **136.119.54.74** | 8080 | ✅ Active |
| **ui** | ClusterIP | 34.118.235.52 | - | 3000 | ✅ Active |
| **customer-auth** | ClusterIP | 34.118.239.160 | - | 8000 | ✅ Active |
| **accounts** | ClusterIP | 34.118.239.30 | - | 50051 | ✅ Active |
| **transactions** | ClusterIP | 34.118.237.38 | - | 50052 | ✅ Active |
| **dashboard** | ClusterIP | 34.118.228.89 | - | 5000 | ✅ Active |

### Kubernetes Pods

| Pod | Status | Node IP | Age | Restarts |
|-----|--------|---------|-----|----------|
| nginx-7cbc86f5bc-xrwnx | ✅ Running | 10.12.0.31 | 54s | 0 |
| ui-d4c4c7b4c-vvkxz | ✅ Running | 10.12.2.27 | 3d1h | 0 |
| customer-auth-cb49449d8-7kvxg | ✅ Running | 10.12.1.24 | 3d1h | 0 |
| accounts-77678bf974-pfmnv | ✅ Running | 10.12.2.26 | 3d1h | 0 |
| transactions-679567fb97-6jkjv | ✅ Running | 10.12.1.23 | 3d1h | 0 |
| dashboard-6bc94449c-pgxmt | ✅ Running | 10.12.2.29 | 8h | 0 |

**All pods:** 6/6 Running ✅

### Horizontal Pod Autoscaler (HPA)

| Service | CPU Target | Current | Min | Max | Replicas | Status |
|---------|-----------|---------|-----|-----|----------|--------|
| accounts | 70% | 4% | 1 | 5 | 1 | ✅ Active |
| transactions | 70% | 4% | 1 | 5 | 1 | ✅ Active |
| customer-auth | 70% | 0% | 1 | 3 | 1 | ✅ Active |
| dashboard | 70% | 1% | 1 | 3 | 1 | ✅ Active |
| ui | 70% | 10% | 1 | 3 | 1 | ✅ Active |
| nginx | 70% | 0% | 1 | 3 | 1 | ✅ Active |

**All HPAs:** 6/6 Active ✅

### Cloud Functions

| Function | Status | URL | Region |
|----------|--------|-----|--------|
| loan-request | ✅ ACTIVE | https://loan-request-gcb4q3froa-uc.a.run.app | us-central1 |
| loan-history | ✅ ACTIVE | https://loan-history-gcb4q3froa-uc.a.run.app | us-central1 |
| atm-locator-service | ✅ ACTIVE | https://atm-locator-service-gcb4q3froa-uc.a.run.app | us-central1 |

**All Functions:** 3/3 Active ✅

### Database Status

```
Database: bank
Collection: atms
Total ATMs: 13
Open ATMs: 10
Interplanetary ATMs: 2
Status: ✅ Populated
```

---

## 🏛️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet Users                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         GCP Load Balancer (External)                        │
│         IP: 136.119.54.74:8080                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Google Kubernetes Engine (GKE)                        │
│         Cluster: martianbank-cluster                          │
│         Zone: us-central1-a                                   │
│         Nodes: 3x e2-medium                                   │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   NGINX      │ │     UI       │ │  Dashboard   │
│ (LoadBalancer)│ │  (React)     │ │  (Flask)     │
│   HPA: 1-3   │ │  HPA: 1-3    │ │  HPA: 1-3    │
└──────┬───────┘ └──────────────┘ └──────┬───────┘
       │                                   │
       ▼                                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Customer-Auth │ │  Accounts    │ │ Transactions │
│  (Node.js)   │ │  (Flask)     │ │  (Flask)     │
│  HPA: 1-3    │ │  HPA: 1-5    │ │  HPA: 1-5    │
└──────────────┘ └──────────────┘ └──────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Compute Engine VM (mongodb-vm)                       │
│         IP: 10.128.0.2:27017                                 │
│         MongoDB: Running                                     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Google Cloud Functions                               │
│         - loan-request                                       │
│         - loan-history                                        │
│         - atm-locator-service                                 │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

**User Registration/Login:**
```
User → Load Balancer → NGINX → customer-auth → MongoDB
```

**Account Operations:**
```
User → Load Balancer → NGINX → dashboard → accounts → MongoDB
```

**Transactions:**
```
User → Load Balancer → NGINX → dashboard → transactions → MongoDB
```

**Loan Application:**
```
User → Load Balancer → NGINX → Cloud Function (loan-request) → MongoDB
```

**ATM Search:**
```
User → Load Balancer → NGINX → Cloud Function (atm-locator) → MongoDB
```

---

## 🔗 Access Points & URLs

### Application Endpoints

| Endpoint | URL | Description |
|----------|-----|-------------|
| **Main Application** | http://136.119.54.74:8080 | React UI (Frontend) |
| **User Registration** | http://136.119.54.74:8080/api/users | POST - Register new user |
| **User Login** | http://136.119.54.74:8080/api/users/auth | POST - Authenticate user |
| **Account Creation** | http://136.119.54.74:8080/api/account | POST - Create account |
| **Transactions** | http://136.119.54.74:8080/api/transaction | POST - Process transaction |
| **Loan Request** | http://136.119.54.74:8080/api/loan | POST - Apply for loan |
| **Loan History** | http://136.119.54.74:8080/api/loanhistory | POST - Get loan history |
| **ATM Locator** | http://136.119.54.74:8080/api/atm | POST - Search ATMs |

### Cloud Function URLs

| Function | URL | Method | Description |
|----------|-----|--------|-------------|
| **Loan Request** | https://loan-request-gcb4q3froa-uc.a.run.app | POST | Process loan application |
| **Loan History** | https://loan-history-gcb4q3froa-uc.a.run.app | POST | Retrieve loan history |
| **ATM Locator** | https://atm-locator-service-gcb4q3froa-uc.a.run.app/api/atm | POST | Search for ATMs |

### Internal Service URLs (ClusterIP)

These are only accessible from within the Kubernetes cluster:

| Service | Internal URL | Port |
|---------|--------------|------|
| ui | http://ui:3000 | 3000 |
| customer-auth | http://customer-auth:8000 | 8000 |
| accounts | http://accounts:50051 | 50051 |
| transactions | http://transactions:50052 | 50052 |
| dashboard | http://dashboard:5000 | 5000 |
| nginx | http://nginx:8080 | 8080 |

### Database Connection

```
Connection String:
mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin

Collections:
- users
- accounts
- transactions
- loans
- atms (13 records populated)
```

---

## 💻 Development Workflow

### Prerequisites

1. **GCP CLI** installed and authenticated
   ```bash
   gcloud auth login
   gcloud config set project cmpe48a-term-project
   ```

2. **kubectl** configured
   ```bash
   gcloud container clusters get-credentials martianbank-cluster \
     --zone=us-central1-a
   ```

3. **Helm** installed
   ```bash
   brew install helm  # macOS
   # or download from https://helm.sh/docs/intro/install/
   ```

4. **Docker** (optional, for local testing)

### Project Structure

```
cmpe48a_term_project/
├── accounts/              # Accounts microservice (Python/gRPC)
├── atm-locator/           # ATM Locator (original, now Cloud Function)
├── cloud-functions/        # Cloud Functions code
│   ├── loan/              # Loan Cloud Function
│   └── atm-locator/       # ATM Locator Cloud Function
├── customer-auth/         # Authentication service (Node.js)
├── dashboard/             # Dashboard service (Flask)
├── loan/                  # Loan service (original, now Cloud Function)
├── martianbank/           # Helm chart
│   ├── templates/         # Kubernetes templates
│   └── values.yaml        # Configuration values
├── nginx/                 # NGINX reverse proxy
├── performance_locust/    # Performance testing scripts
├── scripts/               # Deployment scripts
│   ├── deploy.sh          # Main deployment script
│   ├── rebuild_images.sh  # Rebuild Docker images
│   └── populate_atms_mongosh.sh  # Populate ATM data
├── transactions/          # Transactions microservice (Python/gRPC)
└── ui/                    # React frontend
```

### Common Development Tasks

#### 1. Rebuild and Deploy a Service

```bash
# Rebuild specific service image
./scripts/rebuild_images.sh <service-name>

# Available services: ui, customer-auth, nginx, accounts, transactions, dashboard

# Redeploy after rebuild
./scripts/deploy.sh 123456789
```

#### 2. View Logs

```bash
# View logs for a specific pod
kubectl logs -n martianbank <pod-name> --tail=100

# View logs for all pods of a service
kubectl logs -n martianbank -l app=<service-name> --tail=100

# Follow logs in real-time
kubectl logs -n martianbank <pod-name> -f
```

#### 3. Check Service Status

```bash
# All pods
kubectl get pods -n martianbank

# All services
kubectl get services -n martianbank

# All HPAs
kubectl get hpa -n martianbank

# Detailed pod information
kubectl describe pod <pod-name> -n martianbank
```

#### 4. Update Configuration

```bash
# Edit Helm values
vim martianbank/values.yaml

# Apply changes
helm upgrade martianbank ./martianbank \
  --namespace martianbank \
  --set DB_URL="mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin" \
  --set JWT_SECRET="$(openssl rand -hex 32)"
```

#### 5. Scale Services Manually

```bash
# Scale a deployment
kubectl scale deployment <deployment-name> --replicas=3 -n martianbank

# HPA will adjust automatically, but you can override temporarily
```

#### 6. Access Pod Shell

```bash
# Execute command in pod
kubectl exec -it <pod-name> -n martianbank -- /bin/bash

# Or for specific service
kubectl exec -it -n martianbank -l app=dashboard -- /bin/bash
```

---

## 🛠️ Common Tasks

### Deploy Application

```bash
# Full deployment
./scripts/deploy.sh 123456789
```

This script:
1. Detects MongoDB VM IP automatically
2. Creates namespace if needed
3. Deploys Helm chart with all services
4. Waits for LoadBalancer IP assignment
5. Shows deployment status

### Rebuild Docker Images

```bash
# Rebuild all images
./scripts/rebuild_images.sh

# Rebuild specific service
./scripts/rebuild_images.sh nginx
./scripts/rebuild_images.sh dashboard
```

**Note:** Images are built using GCP Cloud Build, which automatically builds for `linux/amd64` platform.

### Populate ATM Data

```bash
# Populate MongoDB with ATM data
./scripts/populate_atms_mongosh.sh 123456789

# This will insert 13 ATM records into the database
```

### Update Cloud Functions

```bash
# Navigate to function directory
cd cloud-functions/loan  # or cloud-functions/atm-locator

# Deploy function
gcloud functions deploy loan-request \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_loan_request \
  --trigger-http \
  --allow-unauthenticated \
  --vpc-connector=loan-connector \
  --set-env-vars="DB_URL=mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin"
```

### Test Endpoints

```bash
# Test loan request
curl -X POST http://136.119.54.74:8080/api/loan \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "account_type": "checking",
    "account_number": "12345",
    "govt_id_type": "ssn",
    "govt_id_number": "123456789",
    "loan_type": "personal",
    "loan_amount": "1000",
    "interest_rate": "5.0",
    "time_period": "12"
  }'

# Test ATM locator
curl -X POST http://136.119.54.74:8080/api/atm \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Monitor HPA Scaling

```bash
# Watch HPA status
watch kubectl get hpa -n martianbank

# View HPA events
kubectl describe hpa <hpa-name> -n martianbank
```

### Check Resource Usage

```bash
# Pod resource usage
kubectl top pods -n martianbank

# Node resource usage
kubectl top nodes
```

---

## 🔧 Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n martianbank

# Describe pod for details
kubectl describe pod <pod-name> -n martianbank

# Check logs
kubectl logs <pod-name> -n martianbank
```

**Common Issues:**
- **ImagePullBackOff:** Image not found or authentication issue
- **CrashLoopBackOff:** Application error, check logs
- **Pending:** Resource constraints or scheduling issues

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n martianbank

# Test service from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -n martianbank -- \
  wget -qO- http://<service-name>:<port>
```

### Database Connection Issues

```bash
# Test MongoDB connection from pod
kubectl run -it --rm mongo-test --image=mongo:latest --restart=Never -n martianbank -- \
  mongosh "mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin"

# Check MongoDB VM status
gcloud compute instances describe mongodb-vm --zone=us-central1-a

# Check MongoDB service on VM
gcloud compute ssh mongodb-vm --zone=us-central1-a --command="sudo systemctl status mongod"
```

### Load Balancer IP Not Assigned

```bash
# Check service status
kubectl get service nginx -n martianbank

# Describe service for events
kubectl describe service nginx -n martianbank

# Wait for IP (can take 2-5 minutes)
watch kubectl get service nginx -n martianbank
```

### Cloud Function Not Working

```bash
# Check function status
gcloud functions describe <function-name> --gen2 --region=us-central1

# View function logs
gcloud functions logs read <function-name> --gen2 --region=us-central1 --limit=50

# Test function directly
curl -X POST https://<function-url> \
  -H "Content-Type: application/json" \
  -d '{}'
```

### HPA Not Scaling

```bash
# Check HPA status
kubectl get hpa -n martianbank

# Describe HPA for details
kubectl describe hpa <hpa-name> -n martianbank

# Check if metrics server is running
kubectl get deployment metrics-server -n kube-system
```

**Common Issues:**
- Missing CPU/memory requests in deployment
- Metrics server not installed
- Resource limits too low

---

## 📝 Next Steps

### Immediate (Phase 6: Performance Testing)

1. **Update Locust Test Scripts**
   - Update API URLs in `performance_locust/api_urls.py`
   - Point to Load Balancer IP: `http://136.119.54.74:8080`

2. **Design Test Scenarios**
   - Low load: 10 users, 5 minutes
   - Medium load: 50 users, 10 minutes
   - High load: 100 users, 15 minutes
   - Stress test: 200+ users, 20 minutes

3. **Execute Performance Tests**
   ```bash
   # Enable Locust in Helm
   helm upgrade martianbank ./martianbank \
     --namespace martianbank \
     --set locust.enabled=true \
     --reuse-values
   
   # Or run Locust locally
   cd performance_locust
   locust -f account_locust.py --host=http://136.119.54.74:8080
   ```

4. **Collect Metrics**
   - Response times (p50, p95, p99)
   - Throughput (RPS)
   - Error rates
   - Pod scaling events
   - Resource utilization

### Short-term (Phase 7-8)

1. **Cost Monitoring**
   - Set up billing alerts
   - Create cost dashboard
   - Document actual costs

2. **Documentation**
   - Create architecture diagrams
   - Document performance test results
   - Write deployment guide

### Medium-term (Phase 9-10)

1. **Final Testing**
   - End-to-end testing
   - Feature verification
   - System validation

2. **Demo Video**
   - Record 2-minute demo
   - Show architecture
   - Demonstrate features
   - Display performance metrics

---

## 📞 Quick Command Reference

### Check Status
```bash
# Pods
kubectl get pods -n martianbank

# Services
kubectl get services -n martianbank

# HPAs
kubectl get hpa -n martianbank

# Deployments
kubectl get deployments -n martianbank
```

### View Logs
```bash
# Service logs
kubectl logs -n martianbank -l app=<service-name> --tail=100

# Specific pod
kubectl logs -n martianbank <pod-name> --tail=100 -f
```

### Access Application
```bash
# Get Load Balancer IP
kubectl get service nginx -n martianbank

# Application URL
open http://136.119.54.74:8080
```

### Database Operations
```bash
# Populate ATMs
./scripts/populate_atms_mongosh.sh 123456789

# SSH to MongoDB VM
gcloud compute ssh mongodb-vm --zone=us-central1-a

# Connect to MongoDB
mongosh -u root -p 123456789 --authenticationDatabase admin --host 10.128.0.2:27017
```

### Deployment
```bash
# Full deployment
./scripts/deploy.sh 123456789

# Rebuild images
./scripts/rebuild_images.sh <service-name>

# Update Helm chart
helm upgrade martianbank ./martianbank --namespace martianbank --reuse-values
```

---

## 🔐 Credentials & Secrets

### MongoDB
- **Username:** root
- **Password:** 123456789
- **Database:** bank
- **Auth Source:** admin

### GCP Project
- **Project ID:** cmpe48a-term-project
- **Region:** us-central1
- **Zone:** us-central1-a

### JWT Secret
- Generated during deployment
- Stored in Kubernetes ConfigMap: `configmap-martianbank`

---

## 📚 Additional Resources

### Documentation Files
- `docs/REMAINING_STEPS_GUIDE.md` - Detailed guide for remaining phases
- `docs/CURRENT_PROJECT_STATUS.md` - Detailed status report
- `README.md` - Project overview

### Scripts
- `scripts/deploy.sh` - Main deployment script
- `scripts/rebuild_images.sh` - Rebuild Docker images
- `scripts/populate_atms_mongosh.sh` - Populate ATM data

### Helm Chart
- `martianbank/values.yaml` - Configuration values
- `martianbank/templates/` - Kubernetes templates

---

## ⚠️ Important Notes

1. **MongoDB Password:** The password `123456789` is used throughout. Change it in production.

2. **Load Balancer IP:** The IP `136.119.54.74` may change if the service is deleted and recreated.

3. **Cloud Functions:** All functions use VPC Connector `loan-connector` to access MongoDB.

4. **Image Registry:** All images are stored in `gcr.io/cmpe48a-term-project`.

5. **Budget:** Monitor costs regularly. Current estimated monthly cost: ~$172/month.

6. **Firewall Rules:** MongoDB VM only accepts connections from GKE cluster (10.12.0.0/14).

---

## 🎯 Success Criteria

### Completed ✅
- [x] All services deployed on GKE
- [x] MongoDB running on Compute Engine VM
- [x] Cloud Functions deployed and active
- [x] HPA configured for all services
- [x] Load Balancer configured
- [x] Application accessible externally
- [x] Database populated with test data

### Pending ❌
- [ ] Performance tests executed
- [ ] Performance metrics collected and analyzed
- [ ] Cost monitoring configured
- [ ] Final documentation completed
- [ ] Demo video created

---

**Document Version:** 1.0  
**Last Updated:** December 8, 2025  
**Maintained By:** Development Team

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs:** Always start with pod logs
2. **Verify Status:** Check pod/service status
3. **Review Configuration:** Verify Helm values and ConfigMaps
4. **Test Connectivity:** Test from within cluster
5. **Check Documentation:** Review this guide and other docs

For persistent issues, check:
- GCP Console for resource status
- Kubernetes events: `kubectl get events -n martianbank`
- Service descriptions: `kubectl describe <resource> -n martianbank`

---

**Happy Coding! 🚀**

