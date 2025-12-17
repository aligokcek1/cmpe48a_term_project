# Martian Bank - Cloud-Native Architecture
## CMPE 48A Term Project - Presentation Summary

**Project:** Martian Bank - Microservices Banking Application  
**Cloud Platform:** Google Cloud Platform (GCP)  
**Status:** Production-Ready Deployment  
**Date:** December 2025

---

## 🎯 Project Overview

**Objective:** Design, implement, and evaluate a cloud-native architecture integrating:
- ✅ Containerized workloads on Kubernetes (GKE)
- ✅ Virtual Machines (Compute Engine)
- ✅ Serverless Functions (Cloud Functions)

**Application:** Martian Bank - A microservices-based banking platform with:
- User authentication and account management
- Transaction processing
- Loan applications
- ATM location services

---

## 🏗️ Architecture Overview

### High-Level Architecture

```
Internet Users
    ↓
GCP Load Balancer (136.119.54.74:8080)
    ↓
Google Kubernetes Engine (GKE)
    ├─ NGINX (API Gateway)
    ├─ UI Service (React)
    ├─ Customer-Auth (Node.js)
    ├─ Dashboard (Flask)
    ├─ Accounts Service (Flask/gRPC)
    └─ Transactions Service (Flask/gRPC)
    ↓
Compute Engine VM (MongoDB)
    ↓
Cloud Functions
    ├─ Loan Request
    ├─ Loan History
    └─ ATM Locator
```

### Key Components

#### 1. **Kubernetes (GKE) - Containerized Workloads**
- **Cluster:** `martianbank-cluster` (us-central1-a)
- **Nodes:** 3-6 e2-medium nodes (auto-scaling enabled)
- **Services Deployed:** 6 microservices
- **Auto-scaling:** Horizontal Pod Autoscaler (HPA) configured for all services
- **Load Balancing:** GCP Network Load Balancer

**Services:**
| Service | Technology | Replicas | HPA Range | Status |
|---------|-----------|----------|-----------|--------|
| UI | React | 1 | 1-3 | ✅ |
| Customer-Auth | Node.js | 3 | 1-10 | ✅ |
| Dashboard | Flask | 1 | 1-3 | ✅ |
| Accounts | Flask/gRPC | 1 | 1-5 | ✅ |
| Transactions | Flask/gRPC | 2 | 2-5 | ✅ |
| NGINX | Reverse Proxy | 1 | 1-3 | ✅ |

#### 2. **Virtual Machine (Compute Engine) - MongoDB Database**
- **Instance:** `mongodb-vm`
- **Machine Type:** e2-custom-6-8192 (6 vCPU, 8GB RAM)
- **Zone:** us-central1-a
- **Internal IP:** 10.128.0.2:27017
- **Role:** Primary database for all microservices
- **Collections:** users, accounts, transactions, loans, atms

#### 3. **Serverless Functions (Cloud Functions)**
- **Runtime:** Python 3.11 / Node.js 18
- **Region:** us-central1
- **VPC Connector:** Enabled for MongoDB access

| Function | Runtime | Endpoint | Status |
|----------|---------|----------|--------|
| loan-request | Python 3.11 | https://loan-request-gcb4q3froa-uc.a.run.app | ✅ |
| loan-history | Python 3.11 | https://loan-history-gcb4q3froa-uc.a.run.app | ✅ |
| atm-locator-service | Node.js 18 | https://atm-locator-service-gcb4q3froa-uc.a.run.app | ✅ |

---

## 📊 Deployment Architecture

### Request Flow Examples

**User Authentication:**
```
User → Load Balancer → NGINX → Customer-Auth → MongoDB VM
```

**Transaction Processing:**
```
User → Load Balancer → NGINX → Dashboard → Transactions Service → MongoDB VM
```

**Loan Application (Serverless):**
```
User → Load Balancer → NGINX → Cloud Function (loan-request) → MongoDB VM
```

### Service Discovery & Networking
- **Internal:** Kubernetes ClusterIP services for inter-service communication
- **External:** GCP Load Balancer for public access
- **Database:** MongoDB VM accessible via VPC (internal only)
- **Cloud Functions:** Access MongoDB via VPC Connector

---

## 🚀 Deployment Process

### Infrastructure Setup
1. **GKE Cluster Creation**
   - 3-6 node cluster with auto-scaling
   - Auto-repair and auto-upgrade enabled

2. **MongoDB VM Setup**
   - Custom machine type (6 vCPU, 8GB RAM)
   - Network configuration for GKE access
   - Authentication and firewall rules

3. **Cloud Functions Deployment**
   - VPC Connector configuration
   - Environment variables for database connection
   - HTTP triggers with public access

### Application Deployment
1. **Container Images**
   - Built using GCP Cloud Build
   - Stored in Google Container Registry (GCR)
   - Platform: linux/amd64

2. **Kubernetes Deployment**
   - Helm charts for orchestration
   - ConfigMaps for configuration
   - Horizontal Pod Autoscalers for scaling

3. **Load Balancer**
   - NGINX service with LoadBalancer type
   - External IP assignment
   - Path-based routing configuration

### Deployment Tools
- **Helm:** Package management for Kubernetes
- **GCP Cloud Build:** Automated image building
- **kubectl:** Kubernetes cluster management
- **gcloud CLI:** GCP resource management

---

## 📈 Performance Evaluation

### Testing Framework
- **Tool:** Locust (Python-based load testing)
- **Test Scenarios:** Multiple load levels (20, 50, 100, 200, 300 users)
- **Duration:** 5 minutes per test
- **Metrics Collected:**
  - Request latency (p50, p95, p99)
  - Throughput (requests per second)
  - Error rates
  - Resource utilization (CPU, memory)

### Test Design
**Independent Variables:**
- Concurrent users (20, 50, 100, 200, 300)
- Spawn rate (2-40 users/second)
- Test duration (5 minutes)

**Dependent Variables:**
- Response time (latency)
- Throughput (RPS)
- Error rate
- CPU/Memory utilization
- Pod scaling events

### Key Performance Results

**Cloud Functions Performance:**
- ✅ **ATM Locator:** 0% failure rate, 170ms avg response time
- ✅ **Loan Services:** <1% failure rate, 180-550ms response times
- ✅ **Status:** Production-ready performance

**Microservices Performance:**
- ✅ **Accounts Service:** Stable under all load levels
- ✅ **Customer-Auth:** Optimized with v2 image
- ⚠️ **Transactions:** Performance improvements identified

**Auto-scaling Behavior:**
- HPA successfully scales services based on CPU utilization
- Cluster auto-scaling handles node capacity
- Response times maintained under increasing load

---

## 💰 Cost Analysis

### Monthly Cost Breakdown

| Component | Resource | Monthly Cost |
|-----------|----------|--------------|
| **GKE Cluster** | 3-6x e2-medium nodes | ~$60-120 |
| **Load Balancer** | Network Load Balancer | ~$18 |
| **Compute Engine** | e2-custom-6-8192 VM | ~$122 |
| **Cloud Functions** | Invocations + compute | ~$5-10 |
| **Container Registry** | Image storage | ~$1 |
| **Total** | | **~$206-262/month** |

### Cost Optimization Strategies
- ✅ Cluster auto-scaling (3-6 nodes) reduces idle costs
- ✅ Cloud Functions for infrequent workloads (pay-per-use)
- ✅ Efficient resource allocation with HPA
- ✅ Single Load Balancer (cost-effective routing)

### Budget Compliance
- **GCP Trial Budget:** $300
- **Estimated Monthly Cost:** ~$206-262
- **Status:** ✅ Within budget constraints

---

## 🎯 Key Achievements

### Technical Requirements Met
- ✅ **Containerized Workloads:** 6 microservices on Kubernetes
- ✅ **Virtual Machines:** MongoDB on Compute Engine VM
- ✅ **Serverless Functions:** 3 Cloud Functions deployed
- ✅ **Auto-scaling:** HPA configured for all services
- ✅ **Load Balancing:** GCP Load Balancer implemented

### Architecture Highlights
- **Hybrid Architecture:** Kubernetes + VMs + Serverless
- **Microservices Pattern:** Independent, scalable services
- **API Gateway:** NGINX for unified entry point
- **Service Discovery:** Kubernetes DNS-based
- **Database:** Centralized MongoDB on dedicated VM

### Performance Highlights
- **Scalability:** Auto-scaling from 1-10 replicas per service
- **Reliability:** High availability with multiple replicas
- **Response Times:** Sub-second for most operations
- **Throughput:** Handles 100+ concurrent users effectively

---

## 📋 Deployment Summary

### Infrastructure Components
- **GKE Cluster:** 1 cluster, 3-6 nodes
- **Compute Engine:** 1 VM (MongoDB)
- **Cloud Functions:** 3 functions
- **Load Balancer:** 1 Network Load Balancer
- **Container Registry:** 6+ images

### Application Components
- **Microservices:** 6 services
- **Total Pods:** 9+ pods (with scaling)
- **Services:** 6 Kubernetes services
- **HPAs:** 6 Horizontal Pod Autoscalers

### Access Points
- **Application URL:** http://136.119.54.74:8080
- **Cloud Functions:** 3 HTTPS endpoints
- **Database:** Internal only (10.128.0.2:27017)

---

## 🔧 Technical Implementation Details

### Containerization
- **Base Images:** Official language-specific images
- **Multi-stage Builds:** Optimized image sizes
- **Platform:** linux/amd64 for GKE compatibility
- **Registry:** Google Container Registry (GCR)

### Orchestration
- **Helm Charts:** Template-based deployment
- **ConfigMaps:** Centralized configuration
- **Services:** ClusterIP for internal communication
- **Deployments:** Rolling updates support

### Monitoring & Observability
- **Kubernetes Metrics:** CPU, memory, pod status
- **HPA Metrics:** Real-time scaling decisions
- **Logging:** kubectl logs for debugging
- **Health Checks:** Pod status monitoring

---

## 📊 Performance Metrics Summary

### Response Time Percentiles
- **Cloud Functions:** 170-550ms (p50), 180-1000ms (p95)
- **Microservices:** 150-3000ms (p50), 920-5000ms (p95)
- **Overall:** Sub-second for most operations

### Throughput
- **ATM Locator:** 137,777 requests (0% failure)
- **Loan Services:** High throughput, minimal failures
- **Account Operations:** Stable under load

### Resource Utilization
- **CPU:** Efficient usage with HPA scaling
- **Memory:** Within allocated limits
- **Scaling:** Automatic based on demand

---

## 🎓 Project Deliverables Status

### ✅ Completed Deliverables
- [x] **Working System:** Fully deployed on GCP
- [x] **Architecture Diagram:** Documented in report
- [x] **Component Description:** Detailed in documentation
- [x] **Deployment Process:** Step-by-step guides available
- [x] **Locust Tests:** Multiple test scenarios implemented
- [x] **Performance Results:** Metrics collected and analyzed
- [x] **Cost Breakdown:** Detailed cost analysis
- [x] **GitHub Repository:** Code and scripts organized
- [x] **README.md:** Setup instructions provided

### 📝 Documentation Available
- Comprehensive Project Report
- Project Status Guide
- Performance Testing Reports
- Deployment Guides
- Architecture Documentation

---

## 🔑 Key Takeaways

### Architecture Decisions
1. **Hybrid Approach:** Kubernetes for core services, Cloud Functions for event-driven operations
2. **Centralized Database:** MongoDB VM for data consistency
3. **API Gateway Pattern:** NGINX for unified routing
4. **Auto-scaling:** Both pod-level (HPA) and cluster-level scaling

### Performance Insights
1. **Cloud Functions:** Excellent for low-frequency, high-latency-tolerant operations
2. **Microservices:** Require careful resource allocation and scaling configuration
3. **Database:** Centralized VM provides consistent performance
4. **Load Balancing:** Single entry point simplifies architecture

### Cost Optimization
1. **Auto-scaling:** Reduces idle resource costs
2. **Serverless:** Pay-per-use model for infrequent operations
3. **Resource Allocation:** Right-sized instances prevent over-provisioning
4. **Monitoring:** Continuous cost tracking and optimization

---

## 📞 Quick Reference

### Access Points
- **Application:** http://136.119.54.74:8080
- **GKE Cluster:** martianbank-cluster (us-central1-a)
- **MongoDB VM:** 10.128.0.2:27017
- **Project ID:** cmpe48a-term-project

### Key Commands
```bash
# Check cluster status
kubectl get all -n martianbank

# View logs
kubectl logs -n martianbank <pod-name>

# Scale service
kubectl scale deployment <name> --replicas=N -n martianbank

# Deploy application
./scripts/deploy.sh <password>
```

---

## 🎯 Project Requirements Compliance

### ✅ Core Requirements
- ✅ Containerized workloads on Kubernetes (6 services)
- ✅ Virtual Machines integrated (MongoDB VM)
- ✅ Serverless Functions (3 Cloud Functions)
- ✅ Performance evaluation with Locust
- ✅ Cost within $300 GCP trial budget

### ✅ Technical Report Requirements
- ✅ Cloud architecture diagram
- ✅ Component descriptions and interactions
- ✅ Step-by-step deployment process
- ✅ Locust experiment design
- ✅ Performance results visualization
- ✅ Results explanation with metrics
- ✅ Cost breakdown

### ✅ Deliverables
- ✅ Working system on GCP
- ✅ Comprehensive technical report
- ✅ GitHub repository with code
- ✅ README.md with instructions
- ✅ Deployment scripts and manifests

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Purpose:** Presentation Summary for CMPE 48A Term Project

---

## 📚 Additional Resources

- **Full Report:** `docs/COMPREHENSIVE_PROJECT_REPORT.md`
- **Status Guide:** `docs/PROJECT_STATUS_GUIDE.md`
- **Performance Reports:** `docs/PERFORMANCE_TESTING_REPORT.md`
- **GitHub Repository:** Available with all source code and scripts

---

**End of Presentation Summary**

