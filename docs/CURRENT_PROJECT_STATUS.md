# Martian Bank - Current Project Status Report

**Date:** December 9, 2025  
**Project:** CMPE 48A Term Project - Martian Bank GCP Deployment  
**Status:** Phase 5 Complete - Performance Testing Completed

---

## Executive Summary

The Martian Bank application has been successfully deployed to Google Cloud Platform (GCP) with a cloud-native architecture. All core microservices are running on Google Kubernetes Engine (GKE) with auto-scaling enabled, MongoDB is hosted on a Compute Engine VM, and the application is accessible via a Load Balancer. The project is approximately **70% complete**. Performance testing has been completed and documented. Cloud Functions deployment remains as the primary next step.

---

## Architecture Overview

### Current Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP Load Balancer                         │
│              External IP: 136.119.54.74:8080                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Kubernetes Engine (GKE)                  │
│              Cluster: martianbank-cluster                    │
│              Zone: us-central1-a                             │
│              Nodes: 3x e2-medium (2 vCPU, 4GB RAM each)     │
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
│         Zone: us-central1-a                                  │
│         Type: e2-small (0.5 vCPU, 2GB RAM)                  │
│         MongoDB: Running on port 27017                       │
│         Internal IP: 10.128.0.2                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Completed Components

### 1. GCP Infrastructure ✅

- **GCP Project:** `cmpe48a-term-project`
- **Region/Zone:** `us-central1-a`
- **APIs Enabled:**
  - Kubernetes Engine API
  - Compute Engine API
  - Container Registry API
  - Cloud Build API
  - Cloud Functions API (enabled, not used yet)

### 2. Database (MongoDB) ✅

- **VM Instance:** `mongodb-vm`
- **Status:** Running
- **Configuration:**
  - Machine Type: e2-small
  - OS: Ubuntu 22.04 LTS
  - MongoDB: Community Edition (installed and configured)
  - Authentication: Enabled (root user)
  - Network: Accessible from GKE cluster
  - Internal IP: `10.128.0.2`
  - Port: `27017`

**Connection String:**
```
mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin
```

### 3. GKE Cluster ✅

- **Cluster Name:** `martianbank-cluster`
- **Type:** Zonal cluster
- **Zone:** `us-central1-a`
- **Node Pool:**
  - 3 nodes (e2-medium: 2 vCPU, 4GB RAM each)
  - Auto-scaling enabled: 2-5 nodes
  - Auto-repair: Enabled
  - Auto-upgrade: Enabled

**Cluster Status:**
- All nodes: Running
- Metrics Server: Installed and operational
- kubectl: Configured and connected

### 4. Container Images ✅

All Docker images have been built for `linux/amd64` platform and pushed to Google Container Registry (GCR):

| Service | Image | Status |
|---------|-------|--------|
| UI | `gcr.io/cmpe48a-term-project/martianbank-ui:latest` | ✅ Built & Pushed |
| Customer-Auth | `gcr.io/cmpe48a-term-project/martianbank-customer-auth:latest` | ✅ Built & Pushed |
| Accounts | `gcr.io/cmpe48a-term-project/martianbank-accounts:latest` | ✅ Built & Pushed |
| Transactions | `gcr.io/cmpe48a-term-project/martianbank-transactions:latest` | ✅ Built & Pushed |
| Dashboard | `gcr.io/cmpe48a-term-project/martianbank-dashboard:latest` | ✅ Built & Pushed |
| NGINX | `gcr.io/cmpe48a-term-project/martianbank-nginx:latest` | ✅ Built & Pushed |

**Build Method:** GCP Cloud Build (ensures correct platform compatibility)

### 5. Kubernetes Deployments ✅

All microservices are deployed and running in the `martianbank` namespace:

| Service | Replicas | Status | Age |
|---------|----------|--------|-----|
| accounts | 1/1 | Running | 17m |
| customer-auth | 1/1 | Running | 12m |
| dashboard | 1/1 | Running | 12m |
| nginx | 1/1 | Running | 4m |
| transactions | 1/1 | Running | 17m |
| ui | 1/1 | Running | 12m |

**Total:** 6/6 pods running successfully

### 6. Services & Networking ✅

| Service | Type | Cluster IP | External IP | Port |
|---------|------|-----------|-------------|------|
| accounts | ClusterIP | 34.118.239.30 | - | 50051 |
| customer-auth | ClusterIP | 34.118.239.160 | - | 8000 |
| dashboard | ClusterIP | 34.118.228.89 | - | 5000 |
| nginx | LoadBalancer | 34.118.231.229 | **136.119.54.74** | 8080 |
| transactions | ClusterIP | 34.118.237.38 | - | 50052 |
| ui | ClusterIP | 34.118.235.52 | - | 3000 |

**Application URL:** `http://136.119.54.74:8080`

### 7. Horizontal Pod Autoscaler (HPA) ✅

All 6 services have HPA configured and active:

| Service | CPU Target | Current CPU | Min Replicas | Max Replicas | Status |
|---------|-----------|-------------|--------------|--------------|--------|
| accounts | 70% | 4% | 1 | 5 | ✅ Active |
| transactions | 70% | 4% | 1 | 5 | ✅ Active |
| customer-auth | 70% | 0% | 1 | 3 | ✅ Active |
| dashboard | 70% | 1% | 1 | 3 | ✅ Active |
| ui | 70% | 10% | 1 | 3 | ✅ Active |
| nginx | 70% | 0% | 1 | 3 | ✅ Active |

**Resource Configuration:**
- All services have CPU/memory requests and limits defined
- Metrics Server collecting metrics successfully
- HPA actively monitoring and ready to scale

### 8. Helm Chart Configuration ✅

- **Chart Name:** `martianbank`
- **Namespace:** `martianbank`
- **Release:** Deployed (Revision 8)
- **Configuration:**
  - Image registry: `gcr.io/cmpe48a-term-project`
  - MongoDB: Disabled (using external VM)
  - NGINX: Enabled
  - Service Protocol: HTTP
  - ConfigMap: Configured with MongoDB connection string

**Key Files Updated:**
- `martianbank/values.yaml` - Cloud Functions placeholders added
- `martianbank/templates/k8.yaml` - All services configured
- `martianbank/templates/accounts.yaml` - Resource limits added
- `martianbank/templates/transactions.yaml` - Resource limits added
- `martianbank/templates/configmap.yaml` - MongoDB connection configured

### 9. Configuration Management ✅

**ConfigMap (`configmap-martianbank`):**
- `DB_URL`: `mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin`
- `JWT_SECRET`: Generated and configured

**Environment Variables:**
- All services properly configured with environment variables
- Database connectivity verified
- Service-to-service communication working

### 10. Scripts & Automation ✅

**Deployment Scripts:**
- `scripts/deploy.sh` - Main deployment script (auto-detects MongoDB IP)
- `scripts/rebuild_images.sh` - Rebuild images using Cloud Build

**Scripts Removed (cleaned up):**
- Redundant build/deploy scripts removed
- Only essential scripts remain

---

## Pending Components

### 1. Cloud Functions ❌

**Status:** Not Started

**Required Functions:**
- **Loan Service** - Convert from Kubernetes deployment to Cloud Function
- **ATM Locator Service** - Convert from Kubernetes deployment to Cloud Function

**Current State:**
- Loan and ATM-Locator removed from Kubernetes deployments
- NGINX configured to proxy to dashboard (temporary workaround)
- Dashboard environment variables have placeholder Cloud Function URLs
- No Cloud Functions deployed yet

**Impact:**
- Loan application feature not functional
- ATM location search not functional
- Application partially functional (core banking features work)

### 2. Performance Testing ✅

**Status:** Completed

**Completed Work:**
- Updated Locust test scripts with GCP endpoints
- Configured test scenarios (4 load levels: 10, 50, 100, 200 users)
- Executed comprehensive performance tests across all services
- Collected and analyzed 221,085+ total requests
- Created detailed documentation and visualizations

**Results:**
- Performance testing completed across all microservices
- Detailed findings documented in `PERFORMANCE_TESTING_REPORT.md`
- Test results include success rates, response times, and throughput metrics

### 3. Cost Monitoring ❌

**Status:** Not Started

**Required Work:**
- Set up billing alerts
- Create cost tracking dashboard
- Document actual costs
- Implement cost optimization

### 4. Documentation ❌

**Status:** Partial

**Completed:**
- Deployment guides created
- Architecture documented in this file

**Pending:**
- Architecture diagrams (visual)
- Performance test documentation
- Cost analysis documentation
- Final deployment guide

### 5. Final Testing ❌

**Status:** Not Started

**Required Work:**
- End-to-end testing
- Feature verification
- System validation
- Bug fixes (if any)

### 6. Demo Video ❌

**Status:** Not Started

**Required Work:**
- Create 2-minute demo video
- Record screen captures
- Edit and finalize

---

## Technical Details

### Network Configuration

**VPC & Networking:**
- Default VPC network used
- GKE cluster and MongoDB VM in same VPC
- Firewall rules configured for MongoDB access
- Load Balancer configured for external access

**Security:**
- MongoDB authentication enabled
- Services communicate via ClusterIP (internal)
- Only NGINX exposed externally via LoadBalancer

### Resource Allocation

**GKE Cluster:**
- Total CPU: 6 vCPU (3 nodes × 2 vCPU)
- Total Memory: 12GB (3 nodes × 4GB)
- Current Usage: ~20% CPU, ~50% Memory

**MongoDB VM:**
- CPU: 0.5 vCPU
- Memory: 2GB
- Disk: 40GB standard persistent disk

**Pod Resources:**
- Accounts/Transactions: 100m CPU request, 500m limit
- Other services: 50-100m CPU request, 200-500m limit
- Memory: 64-128Mi request, 256-512Mi limit

### Database Status

**MongoDB:**
- Version: Community Edition (latest)
- Database: `bank`
- Collections: Configured and ready
- Connectivity: Verified from all services
- Authentication: Working correctly

---

## Known Issues & Workarounds

### 1. Cloud Functions Not Deployed
**Issue:** Loan and ATM services not available  
**Workaround:** NGINX proxies to dashboard (temporary)  
**Impact:** Loan and ATM features non-functional  
**Solution:** Deploy Cloud Functions (Phase 3)

### 2. NGINX Configuration
**Issue:** NGINX config has placeholder Cloud Function URLs  
**Status:** Fixed to proxy to dashboard temporarily  
**Action Required:** Update with actual Cloud Function URLs after deployment

### 3. Dashboard Environment Variables
**Issue:** Dashboard has placeholder Cloud Function URLs  
**Status:** Configured but pointing to placeholders  
**Action Required:** Update after Cloud Functions deployment

---

## Cost Analysis (Current)

### Monthly Estimated Costs

| Component | Configuration | Estimated Cost |
|-----------|--------------|----------------|
| GKE Nodes | 3x e2-medium | ~$139.20/month |
| MongoDB VM | 1x e2-small | ~$11.10/month |
| Load Balancer | Standard | ~$18.25/month |
| Storage | 40GB disk | ~$4.00/month |
| Cloud Functions | 0 deployed | $0.00/month |
| **Total** | | **~$172.55/month** |

**Budget:** $300/month  
**Remaining:** ~$127.45 buffer

**Note:** Costs will increase slightly when Cloud Functions are deployed, but should remain within budget.

---

## Deployment Commands Reference

### Check Status
```bash
# Pods
kubectl get pods -n martianbank

# Services
kubectl get services -n martianbank

# HPA
kubectl get hpa -n martianbank

# Deployments
kubectl get deployments -n martianbank
```

### Access Application
```bash
# External URL
http://136.119.54.74:8080

# Check Load Balancer IP
kubectl get service nginx -n martianbank
```

### View Logs
```bash
# Service logs
kubectl logs -n martianbank -l app=<service-name>

# Specific pod
kubectl logs -n martianbank <pod-name>
```

### Update Deployment
```bash
# Redeploy with Helm
./scripts/deploy.sh <mongodb-password>
```

---

## Next Steps Summary

1. **Immediate:** Deploy Cloud Functions (Loan & ATM Locator)
2. **Short-term:** Update NGINX and dashboard with Cloud Function URLs
3. **Medium-term:** Performance testing with Locust
4. **Long-term:** Documentation, cost monitoring, demo video

---

## Success Metrics

### Completed ✅
- [x] All core services deployed on GKE
- [x] MongoDB running on Compute Engine VM
- [x] HPA configured for all services
- [x] Load Balancer configured and accessible
- [x] All services communicating correctly
- [x] Application accessible externally

### Pending ❌
- [ ] Cloud Functions deployed (Loan & ATM)
- [x] Performance tests executed
- [ ] Cost monitoring configured
- [ ] Documentation completed
- [ ] Demo video created

---

## Project Health

**Overall Status:** 🟢 **Healthy**

- All core services running
- No critical errors
- Auto-scaling configured
- Application accessible
- Database connectivity verified

**Blockers:** None  
**Risks:** Low (Cloud Functions deployment is straightforward)

---

**Last Updated:** December 5, 2025  
**Document Version:** 1.0

