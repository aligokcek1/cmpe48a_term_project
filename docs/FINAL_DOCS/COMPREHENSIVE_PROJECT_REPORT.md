# Martian Bank - Comprehensive Project Report

**Last Updated:** December 8, 2025  
**Project:** CMPE 48A Term Project - Martian Bank GCP Deployment  
**Status:** Production-Ready with Performance Optimizations  

---

## 📋 Executive Summary

Martian Bank is a cloud-native microservices banking application successfully deployed on Google Cloud Platform. The system demonstrates a hybrid architecture combining Kubernetes-managed microservices with serverless Cloud Functions, all backed by a MongoDB database running on Compute Engine.

### Key Achievements
- ✅ **6 Microservices** deployed on GKE with selective auto-scaling
- ✅ **3 Cloud Functions** for serverless operations
- ✅ **MongoDB** on dedicated Compute Engine VM (2 vCPU, 2GB RAM)
- ✅ **Horizontal Pod Autoscaler (HPA)** configured for transactions and customer-auth services
- ✅ **GCP Load Balancer** providing external access
- ✅ **NGINX** as internal API gateway routing to services and Cloud Functions
- ✅ **Performance Testing** completed with identified optimization opportunities

### Current Infrastructure Status
- **GKE Cluster:** 3 nodes (no auto-scaling), running stable
- **Services:** 6/6 operational with selective HPA (transactions: 1-3, customer-auth: 2-2)
- **Cloud Functions:** 3/3 active and responding
- **Database:** MongoDB operational with 13 ATM records
- **Load Balancer:** Active at `136.119.54.74:8080`

---

## 🏗️ Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Internet Users                               │
└────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              GCP Network Load Balancer (Layer 4)                    │
│              External IP: 136.119.54.74:8080                        │
│              Type: LoadBalancer (Kubernetes Service)                 │
└────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Google Kubernetes Engine (GKE)                          │
│              Cluster: martianbank-cluster                            │
│              Zone: us-central1-a                                     │
│              Nodes: 3x e2-medium (2 vCPU, 4GB RAM each)            │
│              Auto-scaling: Disabled (fixed 3 nodes)                │
│              Total Capacity: ~2.8 vCPUs allocatable                │
└────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              NGINX Service (LoadBalancer)                           │
│              Pod: nginx-7cbc86f5bc-xrwnx                            │
│              IP: 10.12.0.31                                         │
│              Port: 8080                                              │
│              Replicas: 1, No HPA                                      │
│              Role: Internal API Gateway / Reverse Proxy             │
└────────────────────────────┬────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  UI Service  │    │Customer-Auth │    │  Dashboard   │
│  (React)     │    │  (Node.js)   │    │  (Flask)     │
│  Port: 3000  │    │  Port: 8000  │    │  Port: 5000  │
│  Replicas: 1 │    │  Replicas: 2 │    │  Replicas: 1 │
│  No HPA      │    │  HPA: 2-2    │    │  No HPA      │
│  Image:      │    │  Image: v2   │    │  Image:      │
│  latest      │    │              │    │  latest      │
└──────────────┘    └──────┬───────┘    └──────┬───────┘
                           │                    │
                           │                    ├──────────────┐
                           │                    │              │
                           │                    ▼              ▼
                           │            ┌──────────────┐ ┌──────────────┐
                           │            │  Accounts    │ │ Transactions │
                           │            │  (Flask)     │ │  (Flask)     │
                           │            │  Port: 50051 │ │  Port: 50052 │
                           │            │  Replicas: 1 │ │  Replicas: 1 │
                           │            │  No HPA      │ │  HPA: 1-3    │
                           │            │  Image:      │ │  Image: v2   │
                           │            │  latest      │ │              │
                           │            └──────┬───────┘ └──────┬───────┘
                           │                   │                │
                           │                   └────────┬───────┘
                           │                            │
                           └────────────────────────────┼──────────────┐
                                                        │              │
                                                        ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         Compute Engine VM (mongodb-vm)                               │
│         Machine Type: e2-small (2 vCPU, 2GB RAM)                   │
│         Internal IP: 10.128.0.2:27017                               │
│         Status: RUNNING                                               │
│         Database: bank                                               │
│         Collections: users, accounts, transactions, loans, atms      │
└─────────────────────────────────────────────────────────────────────┘
                                                        │
                                                        │
        ┌───────────────────────────────────────────────┼───────────────┐
        │                                               │               │
        ▼                                               ▼               ▼
┌──────────────────────┐    ┌──────────────────────┐  ┌──────────────────────┐
│  Cloud Function:     │    │  Cloud Function:     │  │  Cloud Function:     │
│  loan-request        │    │  loan-history        │  │  atm-locator-service │
│  Runtime: Python 311│    │  Runtime: Python 311 │  │  Runtime: Node.js 18 │
│  Region: us-central1│    │  Region: us-central1│  │  Region: us-central1 │
│  URL:                │    │  URL:                │  │  URL:                │
│  loan-request-       │    │  loan-history-       │  │  atm-locator-        │
│  gcb4q3froa-uc.a.    │    │  gcb4q3froa-uc.a.    │  │  service-gcb4q3froa-  │
│  run.app             │    │  run.app             │  │  uc.a.run.app        │
│  VPC Connector:      │    │  VPC Connector:      │  │  VPC Connector:      │
│  loan-connector      │    │  loan-connector     │  │  loan-connector     │
└──────────────────────┘    └──────────────────────┘  └──────────────────────┘
```

### Request Flow Patterns

#### 1. User Authentication Flow
```
User Browser
    ↓ HTTP POST /api/users/auth
GCP Load Balancer (136.119.54.74:8080)
    ↓
NGINX Pod (10.12.0.31:8080)
    ↓ Route: /api/users → customer-auth:8000
Customer-Auth Service (2 replicas, fixed)
    ↓ MongoDB Query
MongoDB VM (10.128.0.2:27017)
    ↓ JWT Token Response
User Browser
```

#### 2. Account Creation Flow
```
User Browser
    ↓ HTTP POST /api/account
GCP Load Balancer
    ↓
NGINX Pod
    ↓ Route: /api/account → dashboard:5000
Dashboard Service
    ↓ gRPC/HTTP Call
Accounts Service (1 replica, HPA: 1-5)
    ↓ MongoDB Insert
MongoDB VM
    ↓ Response
User Browser
```

#### 3. Transaction Processing Flow
```
User Browser
    ↓ HTTP POST /api/transaction
GCP Load Balancer
    ↓
NGINX Pod
    ↓ Route: /api/transaction → dashboard:5000
Dashboard Service
    ↓ gRPC/HTTP Call
Transactions Service (1 replica, HPA: 1-3, can scale to 3)
    ↓ MongoDB Transaction
MongoDB VM
    ↓ Response
User Browser
```

#### 4. Loan Application Flow (Cloud Function)
```
User Browser
    ↓ HTTP POST /api/loan
GCP Load Balancer
    ↓
NGINX Pod
    ↓ Route: /api/loan → HTTPS Cloud Function
Cloud Function: loan-request
    ↓ VPC Connector
MongoDB VM (10.128.0.2:27017)
    ↓ Response
User Browser
```

#### 5. ATM Locator Flow (Cloud Function)
```
User Browser
    ↓ HTTP POST /api/atm
GCP Load Balancer
    ↓
NGINX Pod
    ↓ Route: /api/atm → HTTPS Cloud Function
Cloud Function: atm-locator-service
    ↓ VPC Connector
MongoDB VM (10.128.0.2:27017)
    ↓ Response (13 ATM records)
User Browser
```

---

## 📊 Infrastructure Details

### Google Kubernetes Engine (GKE)

**Cluster Configuration:**
```
Name: martianbank-cluster
Location: us-central1-a
Status: RUNNING
Master IP: 34.9.197.138
Node Pool: default-pool
  - Node Count: 3 (fixed, no auto-scaling)
  - Machine Type: e2-medium (2 vCPU, 4GB RAM per node)
  - Total vCPUs: 6 (allocatable: ~2.8 vCPUs)
  - Total Memory: 12GB (allocatable: ~9GB)
  - Auto-scaling: Disabled
  - Auto-repair: Enabled
  - Auto-upgrade: Enabled
  - Disk Size: 40GB per node (pd-balanced)
```

**Node Details:**
- 3 nodes in default-pool
- Each node: e2-medium (2 vCPU, 4GB RAM)
- Disk: 40GB pd-balanced per node
- Total pods distributed across 3 nodes

**Namespace:** `martianbank`

### Compute Engine - MongoDB VM

**VM Configuration:**
```
Instance Name: mongodb-vm
Zone: us-central1-a
Status: RUNNING
Machine Type: e2-small
  - vCPUs: 2
  - Memory: 2GB RAM
Internal IP: 10.128.0.2
External IP: None (internal only)
OS: Ubuntu 22.04 LTS
MongoDB Version: Latest
MongoDB Port: 27017
```

**Database Configuration:**
```
Database: bank
Collections:
  - users (authentication data)
  - accounts (bank accounts)
  - transactions (transaction records)
  - loans (loan applications)
  - atms (13 records populated)

Connection String:
mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin
```

**Network Configuration:**
- Firewall: Accepts connections from GKE cluster (10.12.0.0/14)
- Authentication: Enabled (root user)
- Access: Internal only (no external IP)

### Load Balancer

**Configuration:**
```
Service: nginx (LoadBalancer type)
External IP: 136.119.54.74
Port: 8080
Protocol: HTTP
Status: Active
Type: Network Load Balancer (Layer 4)
Backend: NGINX pods in GKE cluster
```

**Application URL:** http://136.119.54.74:8080

### Container Registry

**Registry:** `gcr.io/cmpe48a-term-project`

**Images:**
```
gcr.io/cmpe48a-term-project/martianbank-ui:latest
gcr.io/cmpe48a-term-project/martianbank-customer-auth:v2
gcr.io/cmpe48a-term-project/martianbank-accounts:latest
gcr.io/cmpe48a-term-project/martianbank-transactions:v2
gcr.io/cmpe48a-term-project/martianbank-dashboard:latest
gcr.io/cmpe48a-term-project/martianbank-nginx:latest
```

**Note:** Images are built using GCP Cloud Build for `linux/amd64` platform.

---

## 🔧 Service Details

### 1. UI Service (Frontend)

**Configuration:**
```
Deployment: ui
Replicas: 1 (No HPA)
Image: gcr.io/cmpe48a-term-project/martianbank-ui:latest
Port: 3000
Service Type: ClusterIP
Resources:
  Requests: CPU 100m, Memory 128Mi
  Limits: CPU 500m, Memory 512Mi
```

**Technology:** React + Redux Toolkit + Vite

**Environment Variables:**
- `VITE_USERS_URL`: /api/users
- `VITE_ATM_URL`: /api/atm
- `VITE_ACCOUNTS_URL`: /api/account
- `VITE_TRANSFER_URL`: /api/transaction
- `VITE_LOAN_URL`: /api/loan

**Current Status:** ✅ Running (1 pod)

### 2. Customer-Auth Service

**Configuration:**
```
Deployment: customer-auth
Replicas: 2 (HPA: 2-2, fixed at 2 replicas)
Image: gcr.io/cmpe48a-term-project/customer-auth:v2
Port: 8000
Service Type: ClusterIP
Resources:
  Requests: CPU 100m, Memory 128Mi
  Limits: CPU 500m, Memory 512Mi
```

**Technology:** Node.js + Express

**Endpoints:**
- `POST /api/users/` - User registration
- `POST /api/users/auth` - User login
- `POST /api/users/logout` - User logout
- `PUT /api/users/profile` - Profile updates

**Current Status:** ✅ Running (2 pods)

**Performance:** 
- CPU Usage: 0% (idle)
- HPA Target: 50% CPU
- Fixed Replicas: 2 (no scaling)

### 3. Dashboard Service

**Configuration:**
```
Deployment: dashboard
Replicas: 1 (No HPA)
Image: gcr.io/cmpe48a-term-project/martianbank-dashboard:latest
Port: 5000
Service Type: ClusterIP
Resources:
  Requests: CPU 100m, Memory 128Mi
  Limits: CPU 500m, Memory 512Mi
```

**Technology:** Python + Flask

**Environment Variables:**
- `SERVICE_PROTOCOL`: http
- `ACCOUNT_HOST`: accounts
- `TRANSACTION_HOST`: transactions
- `LOAN_HOST`: https://loan-request-gcb4q3froa-uc.a.run.app
- `ATM_LOCATOR_HOST`: https://atm-locator-service-gcb4q3froa-uc.a.run.app
- `CUSTOMER_AUTH_HOST`: customer-auth
- `DB_URL`: mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin

**Current Status:** ✅ Running (1 pod)

**Performance:**
- CPU Usage: 1%
- No HPA (fixed at 1 replica)

### 4. Accounts Service

**Configuration:**
```
Deployment: accounts
Replicas: 1 (No HPA)
Image: gcr.io/cmpe48a-term-project/martianbank-accounts:latest
Port: 50051 (gRPC)
Service Type: ClusterIP
Resources:
  Requests: CPU 100m, Memory 128Mi
  Limits: CPU 500m, Memory 512Mi
```

**Technology:** Python + Flask + gRPC

**Protocol:** Configurable HTTP or gRPC (via `SERVICE_PROTOCOL` env var)

**Current Status:** ✅ Running (1 pod)

**Performance:**
- CPU Usage: 4%
- No HPA (fixed at 1 replica)

### 5. Transactions Service

**Configuration:**
```
Deployment: transactions
Replicas: 1 (HPA: 1-3, can scale up to 3)
Image: gcr.io/cmpe48a-term-project/transactions:v2
Port: 50052 (gRPC)
Service Type: ClusterIP
Resources:
  Requests: CPU 100m, Memory 128Mi
  Limits: CPU 500m, Memory 512Mi
```

**Technology:** Python + Flask + gRPC

**Protocol:** Configurable HTTP or gRPC (via `SERVICE_PROTOCOL` env var)

**Current Status:** ✅ Running (1 pod, can scale to 3)

**Performance:**
- CPU Usage: 4%
- HPA Target: 50% CPU
- Min Replicas: 1, Max Replicas: 3

### 6. NGINX Service

**Configuration:**
```
Deployment: nginx
Replicas: 1 (No HPA)
Image: gcr.io/cmpe48a-term-project/martianbank-nginx:latest
Port: 8080
Service Type: LoadBalancer (creates GCP Load Balancer)
Resources:
  Requests: CPU 50m, Memory 64Mi
  Limits: CPU 200m, Memory 256Mi
```

**Role:** Internal API Gateway / Reverse Proxy

**Routing Configuration:**
```nginx
/                    → http://ui:3000
/api/users           → http://customer-auth:8000/api/users/
/api/account         → http://dashboard:5000/account/
/api/transaction     → http://dashboard:5000/transaction/
/api/transactionzelle/ → http://dashboard:5000/transaction/zelle/
/api/loan            → https://loan-request-gcb4q3froa-uc.a.run.app/
/api/loanhistory     → https://loan-history-gcb4q3froa-uc.a.run.app/
/api/atm             → https://atm-locator-service-gcb4q3froa-uc.a.run.app/
```

**Current Status:** ✅ Running (1 pod)

**Performance:**
- CPU Usage: 0%
- No HPA (fixed at 1 replica)

---

## ☁️ Cloud Functions

### 1. Loan Request Function

**Configuration:**
```
Name: loan-request
Runtime: Python 3.11
Region: us-central1
URL: https://loan-request-gcb4q3froa-uc.a.run.app
Entry Point: process_loan_request
Trigger: HTTP
Authentication: Unauthenticated (public)
VPC Connector: loan-connector
Environment Variables:
  DB_URL: mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin
```

**Status:** ✅ ACTIVE

**Performance:** Excellent
- Response Time: 410ms (p50), 550ms (p95)
- Failure Rate: <1% under 300-user load
- Throughput: High

### 2. Loan History Function

**Configuration:**
```
Name: loan-history
Runtime: Python 3.11
Region: us-central1
URL: https://loan-history-gcb4q3froa-uc.a.run.app
Entry Point: get_loan_history
Trigger: HTTP
Authentication: Unauthenticated (public)
VPC Connector: loan-connector
Environment Variables:
  DB_URL: mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin
```

**Status:** ✅ ACTIVE

**Performance:** Excellent
- Response Time: 180ms (p50), 190ms (p95)
- Failure Rate: <0.5% under 300-user load
- Throughput: Very High

### 3. ATM Locator Service Function

**Configuration:**
```
Name: atm-locator-service
Runtime: Node.js 18
Region: us-central1
URL: https://atm-locator-service-gcb4q3froa-uc.a.run.app
Entry Point: atmLocator
Trigger: HTTP
Authentication: Unauthenticated (public)
VPC Connector: loan-connector
Environment Variables:
  DB_URL: mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin
```

**Status:** ✅ ACTIVE

**Performance:** Exceptional
- Response Time: 170ms (p50), 180ms (p95)
- Failure Rate: 0% under all load levels
- Throughput: 137,777 requests with 0% failure (tested)

---

## 📈 Horizontal Pod Autoscaler (HPA) Configuration

Selective HPA configuration - only transactions and customer-auth services have HPA enabled:

| Service | Min Replicas | Max Replicas | Target CPU | Current Replicas | Current CPU | Status |
|---------|-------------|--------------|------------|------------------|-------------|--------|
| **accounts** | N/A | N/A | N/A | 1 | 4% | ❌ No HPA |
| **transactions** | 1 | 3 | 50% | 1 | 4% | ✅ Active |
| **customer-auth** | 2 | 2 | 50% | 2 | 0% | ✅ Active (Fixed) |
| **dashboard** | N/A | N/A | N/A | 1 | 1% | ❌ No HPA |
| **ui** | N/A | N/A | N/A | 1 | 11% | ❌ No HPA |
| **nginx** | N/A | N/A | N/A | 1 | 0% | ❌ No HPA |

**HPA Behavior:**
- **transactions**: Scales up when CPU usage exceeds 50% (min: 1, max: 3)
- **customer-auth**: Fixed at 2 replicas (HPA configured but min=max=2)
- Scales down when CPU usage drops below threshold
- Cooldown period: 15 seconds (default)
- Metrics source: Kubernetes Metrics Server

**Current Scaling Status:**
- `customer-auth`: Fixed at 2 replicas (no scaling)
- `transactions`: Running at minimum (1 replica, can scale to 3)
- Other services: Fixed at 1 replica (no HPA)

---

## 🔗 Network Architecture

### Service Discovery

**Internal Service Names (ClusterIP):**
```
ui:              http://ui:3000
customer-auth:   http://customer-auth:8000
dashboard:       http://dashboard:5000
accounts:        http://accounts:50051 (gRPC)
transactions:    http://transactions:50052 (gRPC)
nginx:           http://nginx:8080
```

**External Access:**
```
Application:     http://136.119.54.74:8080
Cloud Functions: HTTPS URLs (see Cloud Functions section)
```

### Network Policies

**Firewall Rules:**
- MongoDB VM: Accepts connections from GKE cluster (10.12.0.0/14)
- GKE Cluster: Internal communication via ClusterIP services
- Load Balancer: Public internet access on port 8080

**VPC Connector:**
- Name: `loan-connector`
- Purpose: Allows Cloud Functions to access MongoDB VM
- Region: us-central1
- Network: Default VPC

---

## 🔐 Security Configuration

### Authentication & Authorization

**JWT Token:**
- Secret: Stored in ConfigMap `configmap-martianbank`
- Algorithm: HS256
- Expiration: Configured per service

**MongoDB Authentication:**
- Username: root
- Password: 123456789 (⚠️ Change in production)
- Auth Source: admin
- Network: Internal only (no external IP)

### Network Security

**Firewall Rules:**
- MongoDB VM: Only accepts connections from GKE cluster IP range
- Load Balancer: Public access on port 8080 (HTTP)
- Cloud Functions: Public HTTPS endpoints (unauthenticated)

---

## 💰 Cost Analysis

### Current Infrastructure Costs (Estimated Monthly)

**GKE Cluster:**
- 3x e2-medium nodes: ~$60/month
- Load Balancer: ~$18/month
- **Subtotal:** ~$78/month

**Compute Engine:**
- 1x e2-small VM: ~$11/month
- **Subtotal:** ~$11/month

**Cloud Functions:**
- Invocations: ~$0.40 per million
- Compute time: ~$0.0000025 per GB-second
- **Subtotal:** ~$5-10/month (estimated)

**Container Registry:**
- Storage: ~$0.026 per GB/month
- **Subtotal:** ~$1/month

**Total Estimated Monthly Cost:** ~$95/month

**Cost Optimization Opportunities:**
1. Use preemptible nodes for non-critical workloads
2. Implement Cloud Function concurrency limits
3. Use Cloud Storage for image storage (cheaper than GCR)

---

## 🚀 Deployment Process

### Current Deployment Scripts

**Main Deployment Script:** `scripts/deploy.sh`
```bash
Usage: ./scripts/deploy.sh [MONGODB_PASSWORD]

Features:
- Auto-detects MongoDB VM IP
- Creates namespace if needed
- Deploys Helm chart with all services
- Configures ConfigMap with DB_URL and JWT_SECRET
- Waits for LoadBalancer IP assignment
- Shows deployment status
```

**Image Rebuild Script:** `scripts/rebuild_images.sh`
```bash
Usage: ./scripts/rebuild_images.sh [service-name]

Features:
- Builds images using GCP Cloud Build
- Automatically builds for linux/amd64 platform
- Pushes to gcr.io/cmpe48a-term-project
- Supports individual service rebuilds
```

**Database Population Script:** `scripts/populate_atms_mongosh.sh`
```bash
Usage: ./scripts/populate_atms_mongosh.sh [MONGODB_PASSWORD]

Features:
- Populates MongoDB with ATM data
- Executes directly on MongoDB VM
- Inserts 13 ATM records
```

### Helm Chart Configuration

**Chart Location:** `martianbank/`

**Key Values (`values.yaml`):**
```yaml
imageRegistry: "gcr.io/cmpe48a-term-project"
SERVICE_PROTOCOL: "http"
mongodb:
  enabled: false  # Using external VM
nginx:
  enabled: true
cloudFunctions:
  loanRequestURL: "https://loan-request-gcb4q3froa-uc.a.run.app"
  loanHistoryURL: "https://loan-history-gcb4q3froa-uc.a.run.app"
  atmLocatorURL: "https://atm-locator-service-gcb4q3froa-uc.a.run.app"
```

**Templates:**
- `k8.yaml` - UI, Dashboard, Customer-Auth, NGINX
- `accounts.yaml` - Accounts service
- `transactions.yaml` - Transactions service
- `hpa.yaml` - Horizontal Pod Autoscaler definitions
- `configmap.yaml` - Configuration management

---

## 📝 API Endpoints

### Public Endpoints (via Load Balancer)

| Endpoint | Method | Description | Backend Service |
|----------|--------|-------------|----------------|
| `/` | GET | React UI | UI Service |
| `/api/users` | POST | User registration | Customer-Auth |
| `/api/users/auth` | POST | User login | Customer-Auth |
| `/api/users/logout` | POST | User logout | Customer-Auth |
| `/api/users/profile` | PUT | Update profile | Customer-Auth |
| `/api/account` | POST | Create account | Dashboard → Accounts |
| `/api/accountallaccounts` | POST | Get all accounts | Dashboard → Accounts |
| `/api/accountdetail` | GET | Account details | Dashboard → Accounts |
| `/api/transaction` | POST | Internal transfer | Dashboard → Transactions |
| `/api/transactionzelle/` | POST | Zelle transfer | Dashboard → Transactions |
| `/api/transactionhistory` | POST | Transaction history | Dashboard → Transactions |
| `/api/loan` | POST | Apply for loan | Cloud Function |
| `/api/loanhistory` | POST | Loan history | Cloud Function |
| `/api/atm` | POST | Search ATMs | Cloud Function |

### Cloud Function Endpoints (Direct Access)

| Function | URL | Method | Description |
|----------|-----|--------|-------------|
| Loan Request | https://loan-request-gcb4q3froa-uc.a.run.app | POST | Process loan application |
| Loan History | https://loan-history-gcb4q3froa-uc.a.run.app | POST | Retrieve loan history |
| ATM Locator | https://atm-locator-service-gcb4q3froa-uc.a.run.app/api/atm | POST | Search for ATMs |

---

## 🔍 Monitoring & Observability

### Current Monitoring

**Kubernetes Metrics:**
- CPU usage per pod
- Memory usage per pod
- Pod status and restarts
- HPA scaling events

**Access Methods:**
```bash
# Pod metrics
kubectl top pods -n martianbank

# Node metrics
kubectl top nodes

# HPA status
kubectl get hpa -n martianbank

# Pod logs
kubectl logs -n martianbank <pod-name> -f
```

### Recommended Monitoring Enhancements

1. **GCP Cloud Monitoring**
   - Set up dashboards for service metrics
   - Configure alerts for high error rates
   - Monitor Cloud Function invocations

2. **Application Logging**
   - Centralized logging (Cloud Logging)
   - Structured logging format
   - Log aggregation and analysis

3. **Distributed Tracing**
   - Implement OpenTelemetry
   - Trace requests across services
   - Identify performance bottlenecks

4. **Health Checks**
   - Implement health endpoints for all services
   - Configure Kubernetes liveness/readiness probes
   - Monitor service dependencies

---

## 📚 Documentation References

### Project Documentation
- `docs/PROJECT_STATUS_GUIDE.md` - Current project status
- `docs/PERFORMANCE_TESTING_REPORT.md` - Performance test results
- `docs/FINAL_TEST_RESULTS_ANALYSIS.md` - Detailed test analysis
- `docs/PERFORMANCE_OPTIMIZATION_REPORT.md` - Optimization recommendations
- `docs/REMAINING_STEPS_GUIDE.md` - Next steps guide

### Architecture Documentation
- `docs/ARCHITECTURE_NGINX_LOADBALANCER.md` - NGINX vs Load Balancer
- `docs/CODEBASE_ANALYSIS.md` - Codebase structure
- `docs/GKE_DEPLOYMENT_GUIDE.md` - Deployment guide

### Scripts
- `scripts/deploy.sh` - Main deployment script
- `scripts/rebuild_images.sh` - Image rebuild script
- `scripts/populate_atms_mongosh.sh` - Database population

---

## 📞 Quick Reference

### Key IPs & URLs

```
Load Balancer:     136.119.54.74:8080
MongoDB VM:        10.128.0.2:27017
GKE Master:        34.9.197.138
Application URL:    http://136.119.54.74:8080
```

### Cloud Function URLs

```
Loan Request:       https://loan-request-gcb4q3froa-uc.a.run.app
Loan History:       https://loan-history-gcb4q3froa-uc.a.run.app
ATM Locator:        https://atm-locator-service-gcb4q3froa-uc.a.run.app
```

### Common Commands

```bash
# Check status
kubectl get all -n martianbank

# View logs
kubectl logs -n martianbank <pod-name> -f

# Scale service
kubectl scale deployment <deployment-name> --replicas=3 -n martianbank

# Deploy
./scripts/deploy.sh 123456789

# Rebuild images
./scripts/rebuild_images.sh <service-name>
```

---




## 🆘 Support & Troubleshooting

For issues or questions:
1. Check pod logs: `kubectl logs -n martianbank <pod-name>`
2. Review service status: `kubectl get all -n martianbank`
3. Check HPA: `kubectl get hpa -n martianbank`
4. Review this document for architecture details
5. Review service logs and metrics for troubleshooting

---

**End of Report**

