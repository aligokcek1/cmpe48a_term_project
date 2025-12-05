# Codebase Analysis - Martian Bank Application

## Application Overview

Martian Bank is a microservices-based banking application that simulates a complete banking system with account management, transactions, loans, ATM location services, and user authentication.

## Current Architecture

### Microservices Breakdown

#### 1. **Frontend (UI)**
- **Technology**: React + Redux Toolkit
- **Location**: `ui/`
- **Port**: 3000
- **Status**: ✅ Ready for GKE deployment
- **Dependencies**: Backend APIs, NGINX reverse proxy

#### 2. **Customer Authentication**
- **Technology**: Node.js + Express
- **Location**: `customer-auth/`
- **Port**: 8000
- **Database**: MongoDB (users collection)
- **Status**: ✅ Ready for GKE deployment
- **Key Features**: JWT authentication, user registration/login

#### 3. **Accounts Service**
- **Technology**: Python + Flask (supports gRPC)
- **Location**: `accounts/`
- **Port**: 50051 (gRPC) / Flask port configurable
- **Database**: MongoDB (accounts collection)
- **Status**: ✅ Ready for GKE deployment with HPA
- **Key Features**: Account creation, account details, account listing
- **Protocol**: Configurable HTTP or gRPC via `SERVICE_PROTOCOL` env var

#### 4. **Transactions Service**
- **Technology**: Python + Flask (supports gRPC)
- **Location**: `transactions/`
- **Port**: 50052 (gRPC) / Flask port configurable
- **Database**: MongoDB (transactions collection)
- **Status**: ✅ Ready for GKE deployment with HPA
- **Key Features**: Money transfers, transaction history
- **Protocol**: Configurable HTTP or gRPC

#### 5. **Dashboard Service**
- **Technology**: Python + Flask
- **Location**: `dashboard/`
- **Port**: 5000
- **Status**: ✅ Ready for GKE deployment
- **Key Features**: Web dashboard, form handling
- **Communication**: Uses gRPC/HTTP to communicate with accounts, transactions, loan services

#### 6. **Loan Service** ⚠️ **TO CONVERT TO CLOUD FUNCTION**
- **Technology**: Python + Flask (supports gRPC)
- **Location**: `loan/`
- **Port**: 50053 (gRPC) / Flask port configurable
- **Database**: MongoDB (loans collection, accounts collection)
- **Status**: ⚠️ Needs conversion to Cloud Function
- **Key Features**: 
  - Loan request processing (`/loan/request` POST)
  - Loan history retrieval (`/loan/history` POST)
- **Conversion Notes**: 
  - Currently Flask-based with two endpoints
  - Needs to be converted to Cloud Function HTTP handlers
  - Must maintain MongoDB connection to VM

#### 7. **ATM Locator Service** ⚠️ **TO CONVERT TO CLOUD FUNCTION**
- **Technology**: Node.js + Express
- **Location**: `atm-locator/`
- **Port**: 8001
- **Database**: MongoDB (atms collection)
- **Status**: ⚠️ Needs conversion to Cloud Function
- **Key Features**: ATM location search, ATM data management
- **Conversion Notes**:
  - Express.js application with routes under `/api/atm`
  - Database seeding on startup (from `atm_data.json`)
  - Needs conversion to Cloud Function format
  - Must maintain MongoDB connection to VM

#### 8. **NGINX Reverse Proxy**
- **Location**: `nginx/`
- **Port**: 8080
- **Status**: ✅ Ready for GKE deployment
- **Function**: Routes traffic to appropriate microservices

#### 9. **MongoDB Database** ⚠️ **TO DEPLOY ON COMPUTE ENGINE VM**
- **Current**: Docker container in docker-compose
- **Status**: ⚠️ Needs deployment on GCE VM
- **Collections**: 
  - `accounts` - User bank accounts
  - `transactions` - Transaction records
  - `loans` - Loan applications
  - `users` - User authentication data
  - `atms` - ATM location data

## Current Deployment Configuration

### Docker Compose Setup
- **File**: `docker-compose.yaml`
- **Purpose**: Local development
- **Services**: All microservices + MongoDB + Locust
- **Network**: `bankapp-network` (bridge)

### Helm Chart Setup
- **Location**: `martianbank/`
- **Chart Version**: 0.1.0
- **Current Templates**:
  - `accounts.yaml` - Accounts deployment + service
  - `transactions.yaml` - Transactions deployment + service
  - `deployment.yaml` - Generic deployment template
  - `service.yaml` - Generic service template
  - `hpa.yaml` - Horizontal Pod Autoscaler template
  - `configmap.yaml` - Configuration management
  - `mongodb.yaml` - MongoDB deployment (needs removal for VM)
  - `ingress.yaml` - Ingress configuration
  - `k8.yaml` - Additional Kubernetes resources

### Configuration Management

#### Environment Variables Required:
- `DB_URL` - MongoDB connection string
- `SERVICE_PROTOCOL` - "http" or "grpc"
- `JWT_SECRET` - Secret for JWT tokens
- `DATABASE_HOST` - Alternative DB host (for local MongoDB)

#### ConfigMap Structure:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: configmap-martianbank
data:
  DB_URL: "mongodb://root:example@mongodb:27017"
  JWT_SECRET: "your-secret-key"
```

## Database Schema Analysis

### MongoDB Collections:

1. **accounts**
   - `account_number` (string, unique)
   - `email_id` (string)
   - `account_type` (string)
   - `name` (string)
   - `balance` (number)
   - `currency` (string)
   - `address` (string)
   - `govt_id_number` (string)
   - `government_id_type` (string)
   - `created_at` (datetime)

2. **transactions**
   - `transaction_id` (ObjectId)
   - `sender_account` (string)
   - `receiver_account` (string)
   - `amount` (number)
   - `timestamp` (datetime)
   - `status` (string)

3. **loans**
   - `name` (string)
   - `email` (string)
   - `account_number` (string)
   - `loan_type` (string)
   - `loan_amount` (number)
   - `interest_rate` (number)
   - `time_period` (string)
   - `status` (string: "Approved" or "Declined")
   - `timestamp` (datetime)

4. **users** (customer-auth)
   - User authentication data
   - Managed by customer-auth service

5. **atms**
   - ATM location data
   - Seeded from `atm-locator/config/atm_data.json`

## Performance Testing Setup

### Locust Test Files:
- **Location**: `performance_locust/`
- **Test Files**:
  - `account_locust.py` - Account service load testing
  - `transaction_locust.py` - Transaction service load testing
  - `loan_locust.py` - Loan service load testing
  - `atm_locust.py` - ATM locator load testing
  - `auth_locust.py` - Authentication load testing
- **Configuration**: `api_urls.py` - API endpoint URLs
- **Status**: ⚠️ Needs URL updates for GCP endpoints

### Current API URLs (Local):
```python
VITE_ACCOUNTS_URL = 'http://127.0.0.1:5000/account'
VITE_USERS_URL = 'http://localhost:8000/api/users'
VITE_ATM_URL = 'http://localhost:8001/api/atm'
VITE_TRANSFER_URL = 'http://127.0.0.1:5000/transaction'
VITE_LOAN_URL = 'http://127.0.0.1:5000/loan'
```

## Key Dependencies & Technologies

### Backend:
- **Python**: Flask, gRPC, pymongo
- **Node.js**: Express, mongoose
- **Protocol Buffers**: gRPC service definitions
- **Database**: MongoDB (PyMongo, Mongoose)

### Frontend:
- **React**: UI framework
- **Redux Toolkit**: State management
- **Vite**: Build tool

### Infrastructure:
- **Docker**: Containerization
- **Kubernetes**: Orchestration (via Helm)
- **NGINX**: Reverse proxy

## Migration Requirements

### For GKE Deployment:
1. ✅ All services are containerized (Dockerfiles exist)
2. ✅ Helm charts are available
3. ⚠️ Need to update image repositories to GCR
4. ⚠️ Need to configure HPA for Accounts and Transactions
5. ⚠️ Need to remove MongoDB from Kubernetes (deploy on VM)

### For Cloud Functions:
1. ⚠️ **Loan Service**: Convert Flask app to Cloud Function
   - Two endpoints to convert
   - Maintain MongoDB connection
   - Handle CORS
   
2. ⚠️ **ATM Locator**: Convert Express app to Cloud Function
   - Express routes to Cloud Function handlers
   - Database seeding logic
   - MongoDB connection

### For VM Deployment:
1. ⚠️ **MongoDB**: Install and configure on GCE VM
   - Network configuration
   - Authentication setup
   - Firewall rules for GKE access
   - Data persistence

## Current Issues & Considerations

### 1. Database Connection
- All services use `DB_URL` environment variable
- Connection string format: `mongodb://user:password@host:port`
- Need to update to VM IP address

### 2. Service Discovery
- Currently uses Docker service names
- Need Kubernetes service names for GKE
- Cloud Functions will use HTTP URLs

### 3. Protocol Support
- Services support both HTTP and gRPC
- Currently configured via `SERVICE_PROTOCOL` env var
- For Cloud Functions, HTTP only (gRPC not supported)

### 4. Image Management
- Currently uses `ghcr.io/cisco-open/martian-bank-demo-*` images
- Need to build and push to GCR/Artifact Registry
- Update Helm chart image references

### 5. Configuration Management
- ConfigMap needs updates for:
  - MongoDB VM connection string
  - Cloud Function URLs
  - Load Balancer IP (for frontend)

## Recommended Migration Order

1. **Phase 1**: GCP setup and MongoDB VM
2. **Phase 2**: Convert Cloud Functions (Loan, ATM)
3. **Phase 3**: Build and push container images
4. **Phase 4**: Deploy GKE cluster
5. **Phase 5**: Deploy remaining services to GKE
6. **Phase 6**: Configure Load Balancer and HPA
7. **Phase 7**: Update and run performance tests

## Code Quality Observations

### Strengths:
- ✅ Well-structured microservices architecture
- ✅ Dockerized and container-ready
- ✅ Helm charts available
- ✅ Environment-based configuration
- ✅ Performance testing framework in place
- ✅ Supports both HTTP and gRPC protocols

### Areas for Improvement:
- ⚠️ Hardcoded image references in Helm charts
- ⚠️ No Terraform/IaC (bonus opportunity)
- ⚠️ Limited error handling documentation
- ⚠️ No health check endpoints documented
- ⚠️ Database connection pooling not explicitly configured

## Next Steps

1. Review this analysis
2. Follow the [GCP_DEPLOYMENT_ROADMAP.md](./GCP_DEPLOYMENT_ROADMAP.md)
3. Start with Phase 1: GCP Project Setup
4. Proceed systematically through each phase

---

**Analysis Date**: [Current Date]
**Codebase Version**: Based on current repository state
**Prepared For**: CMPE 48A Term Project

