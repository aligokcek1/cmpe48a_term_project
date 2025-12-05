# Martian Bank - Remaining Steps Guide

**Date:** December 5, 2025  
**Project:** CMPE 48A Term Project - Martian Bank GCP Deployment  
**Status:** Phase 5 Complete - Remaining Phases 3, 6-10

---

## Overview

This guide provides detailed, step-by-step instructions for completing the remaining phases of the Martian Bank GCP deployment project. The project is currently at **60% completion**, with Cloud Functions deployment and performance testing as the primary remaining tasks.

**Estimated Time to Complete:** 35-50 hours  
**Priority Order:** Phase 3 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10

---

## Phase 3: Cloud Functions Development

**Duration:** 8-10 hours  
**Priority:** HIGH (Required for full functionality)  
**Status:** Not Started

### 3.1 Loan Service Cloud Function

#### Step 1: Analyze Current Loan Service
```bash
# Review the current loan service implementation
cd /Users/aligokcek1/Documents/GitHub/cmpe48a_term_project
cat loan/loan.py
cat loan/requirements.txt
```

**Key Endpoints to Convert:**
- `/loan/request` - Process loan application
- `/loan/history` - Get loan history

#### Step 2: Create Cloud Function Structure
```bash
# Create directory structure
mkdir -p cloud-functions/loan
cd cloud-functions/loan

# Create main.py (Cloud Function entry point)
# Create requirements.txt
# Create .env.yaml (for MongoDB connection)
```

**File Structure:**
```
cloud-functions/
  loan/
    main.py              # Cloud Function entry points
    requirements.txt     # Python dependencies
    .env.yaml           # Environment variables (MongoDB connection)
```

#### Step 3: Convert Flask to Cloud Function

**main.py Template:**
```python
import functions_framework
from flask import jsonify
import os
from pymongo import MongoClient
import json

# MongoDB connection
DB_URL = os.environ.get('DB_URL', 'mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin')
client = MongoClient(DB_URL)
db = client["bank"]
loans_collection = db["loans"]

@functions_framework.http
def process_loan_request(request):
    """Process loan application request"""
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    
    # Get request data
    request_json = request.get_json(silent=True)
    
    # Process loan logic (copy from loan/loan.py)
    # ... your loan processing code ...
    
    # Return response
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    return (jsonify(result), 200, headers)

@functions_framework.http
def get_loan_history(request):
    """Get loan history"""
    # Similar structure to process_loan_request
    # ... implementation ...
```

**requirements.txt:**
```txt
functions-framework==3.*
flask==3.1.2
pymongo==4.15.5
```

#### Step 4: Deploy Loan Cloud Function
```bash
# Set environment variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Deploy the function
cd cloud-functions/loan

gcloud functions deploy loan-service \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=process_loan_request \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --set-env-vars="DB_URL=mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin" \
  --max-instances=10

# Note: You'll need to deploy get_loan_history separately or combine them
```

**Get Function URL:**
```bash
gcloud functions describe loan-service \
  --gen2 \
  --region=$REGION \
  --format="value(serviceConfig.uri)"
```

#### Step 5: Test Loan Function
```bash
# Test the function
curl -X POST https://<function-url> \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com",...}'
```

### 3.2 ATM Locator Cloud Function

#### Step 1: Analyze Current ATM Locator Service
```bash
cd /Users/aligokcek1/Documents/GitHub/cmpe48a_term_project
cat atm-locator/server.js
cat atm-locator/package.json
```

#### Step 2: Create Cloud Function Structure
```bash
mkdir -p cloud-functions/atm-locator
cd cloud-functions/atm-locator
```

**File Structure:**
```
cloud-functions/
  atm-locator/
    index.js           # Cloud Function entry point
    package.json       # Node.js dependencies
    config/
      atm_data.json    # ATM data (if needed)
```

#### Step 3: Convert Express to Cloud Function

**index.js Template:**
```javascript
const functions = require('@google-cloud/functions-framework');
const { MongoClient } = require('mongodb');

const DB_URL = process.env.DB_URL || 'mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin';

functions.http('atmLocator', async (req, res) => {
  // Set CORS headers
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }

  try {
    // Connect to MongoDB
    const client = new MongoClient(DB_URL);
    await client.connect();
    const db = client.db('bank');
    const atmsCollection = db.collection('atms');

    // Handle different routes
    if (req.method === 'POST' && req.path === '/api/atm') {
      // Search ATMs logic (copy from atm-locator/server.js)
      const { latitude, longitude, radius } = req.body;
      // ... your ATM search logic ...
      
      const results = await atmsCollection.find({...}).toArray();
      res.status(200).json(results);
    } else if (req.method === 'GET' && req.path.startsWith('/api/atm/')) {
      // Get specific ATM
      const atmId = req.path.split('/').pop();
      const atm = await atmsCollection.findOne({ _id: atmId });
      res.status(200).json(atm);
    } else {
      res.status(404).json({ error: 'Not found' });
    }

    await client.close();
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});
```

**package.json:**
```json
{
  "name": "atm-locator-function",
  "version": "1.0.0",
  "dependencies": {
    "@google-cloud/functions-framework": "^3.0.0",
    "mongodb": "^6.0.0"
  }
}
```

#### Step 4: Deploy ATM Locator Cloud Function
```bash
cd cloud-functions/atm-locator

gcloud functions deploy atm-locator-service \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=atmLocator \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --set-env-vars="DB_URL=mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin" \
  --max-instances=10
```

**Get Function URL:**
```bash
gcloud functions describe atm-locator-service \
  --gen2 \
  --region=$REGION \
  --format="value(serviceConfig.uri)"
```

### 3.3 Update Application Configuration

#### Step 1: Update Helm Values
```bash
# Get Cloud Function URLs
LOAN_URL=$(gcloud functions describe loan-service --gen2 --region=us-central1 --format="value(serviceConfig.uri)")
ATM_URL=$(gcloud functions describe atm-locator-service --gen2 --region=us-central1 --format="value(serviceConfig.uri)")

# Update values.yaml
cat >> martianbank/values.yaml <<EOF
# Update these with actual URLs
cloudFunctions:
  loanURL: "$LOAN_URL"
  atmLocatorURL: "$ATM_URL"
EOF
```

#### Step 2: Update NGINX Configuration
```bash
# Edit nginx/default.conf
# Update /api/atm location to use Cloud Function URL
# Update /api/loan location if needed
```

**nginx/default.conf update:**
```nginx
location /api/atm {
    proxy_pass https://<atm-locator-function-url>;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_ssl_server_name on;
}

location /api/loan {
    proxy_pass https://<loan-function-url>;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_ssl_server_name on;
}
```

#### Step 3: Rebuild NGINX Image
```bash
./scripts/rebuild_images.sh nginx
```

#### Step 4: Redeploy Application
```bash
helm upgrade martianbank ./martianbank \
  --namespace martianbank \
  --set SERVICE_PROTOCOL=http \
  --set DB_URL="mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin" \
  --set JWT_SECRET="$(openssl rand -hex 32)" \
  --set imageRegistry="gcr.io/cmpe48a-term-project" \
  --set mongodb.enabled=false \
  --set nginx.enabled=true \
  --set cloudFunctions.loanURL="$LOAN_URL" \
  --set cloudFunctions.atmLocatorURL="$ATM_URL"
```

#### Step 5: Verify Cloud Functions Integration
```bash
# Test from browser
# Navigate to http://136.119.54.74:8080
# Test loan application feature
# Test ATM location search
```

**Deliverables:**
- ✅ Loan Cloud Function deployed
- ✅ ATM Locator Cloud Function deployed
- ✅ Application updated to use Cloud Functions
- ✅ All features functional

---

## Phase 6: Performance Testing & Optimization

**Duration:** 10-14 hours  
**Priority:** HIGH (Required for project completion)  
**Status:** Not Started

### 6.1 Locust Test Updates

#### Step 1: Update API URLs
```bash
cd performance_locust
# Edit api_urls.py
```

**api_urls.py:**
```python
ApiUrls = {
    'VITE_ACCOUNTS_URL': 'http://136.119.54.74:8080/api/account',
    'VITE_USERS_URL': 'http://136.119.54.74:8080/api/users',
    'VITE_ATM_URL': 'http://136.119.54.74:8080/api/atm',
    'VITE_TRANSFER_URL': 'http://136.119.54.74:8080/api/transaction',
    'VITE_LOAN_URL': 'http://136.119.54.74:8080/api/loan',
}
```

#### Step 2: Review and Update Test Files
```bash
# Update all Locust test files:
# - account_locust.py
# - transaction_locust.py
# - loan_locust.py
# - atm_locust.py
# - auth_locust.py
```

**Key Updates:**
- Replace localhost URLs with Load Balancer IP
- Update Cloud Function URLs
- Adjust test parameters (users, spawn rate, duration)

#### Step 3: Test Locust Scripts Locally
```bash
# Install Locust
pip install locust

# Test against GCP endpoints
locust -f account_locust.py --host=http://136.119.54.74:8080
```

### 6.2 Performance Test Execution

#### Step 1: Set Up Monitoring
```bash
# Enable Cloud Monitoring
# Create monitoring dashboards in GCP Console
# Set up alerts for high error rates
```

#### Step 2: Design Test Scenarios

**Scenario 1: Low Load**
- Users: 10
- Spawn Rate: 2 users/second
- Duration: 5 minutes
- Purpose: Baseline performance

**Scenario 2: Medium Load**
- Users: 50
- Spawn Rate: 5 users/second
- Duration: 10 minutes
- Purpose: Normal operation

**Scenario 3: High Load**
- Users: 100
- Spawn Rate: 10 users/second
- Duration: 15 minutes
- Purpose: Stress testing

**Scenario 4: Stress Test**
- Users: 200+
- Spawn Rate: 20 users/second
- Duration: 20 minutes
- Purpose: Breaking point

#### Step 3: Execute Tests
```bash
# Run Locust tests
locust -f account_locust.py \
  --host=http://136.119.54.74:8080 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=10m \
  --headless \
  --html=results/account_test.html

# Repeat for each test file
```

#### Step 4: Collect Metrics

**Metrics to Collect:**
- Response times (min, max, avg, p50, p95, p99)
- Requests per second (RPS)
- Error rates (4xx, 5xx)
- Pod count over time (HPA scaling)
- CPU/Memory usage per pod
- Cloud Function invocation metrics
- Database connection pool usage

**Commands:**
```bash
# Monitor pods during test
watch kubectl get pods -n martianbank

# Monitor HPA
watch kubectl get hpa -n martianbank

# Check pod metrics
kubectl top pods -n martianbank

# View Cloud Function metrics in GCP Console
```

#### Step 5: Document Results
- Create charts and graphs
- Analyze performance bottlenecks
- Document findings
- Create performance report

### 6.3 Performance Optimization

#### Step 1: Analyze Bottlenecks
- Review test results
- Identify slow endpoints
- Check resource utilization
- Analyze error patterns

#### Step 2: Optimize Configuration
```bash
# Adjust HPA thresholds if needed
kubectl edit hpa accounts -n martianbank
kubectl edit hpa transactions -n martianbank

# Tune resource requests/limits
# Edit Helm templates if needed
```

#### Step 3: Re-run Tests
- Execute same scenarios
- Compare before/after metrics
- Document improvements

**Deliverables:**
- ✅ Updated Locust test scripts
- ✅ Performance test results
- ✅ Visualizations (charts/graphs)
- ✅ Performance analysis report
- ✅ Optimization documentation

---

## Phase 7: Cost Monitoring & Optimization

**Duration:** 3-5 hours  
**Priority:** MEDIUM  
**Status:** Not Started

### 7.1 Cost Tracking Setup

#### Step 1: Set Up Billing Alerts
```bash
# In GCP Console:
# 1. Navigate to Billing > Budgets & alerts
# 2. Create budget alerts:
#    - Alert at $100
#    - Alert at $200
#    - Alert at $250
```

#### Step 2: Create Cost Breakdown Dashboard
- Use GCP Cost Management
- Track costs by service
- Monitor daily spending

#### Step 3: Document Expected Costs
- Update cost breakdown table
- Compare actual vs. estimated
- Document any discrepancies

### 7.2 Cost Optimization

#### Step 1: Implement Cost-Saving Measures
```bash
# Stop resources when not in use
gcloud compute instances stop mongodb-vm --zone=us-central1-a

# Use preemptible nodes (optional)
# Right-size instances based on usage
```

#### Step 2: Create Resource Management Scripts
```bash
# Create start/stop scripts
# Create cluster scaling scripts
```

**Deliverables:**
- ✅ Billing alerts configured
- ✅ Cost tracking dashboard
- ✅ Cost optimization measures
- ✅ Cost documentation

---

## Phase 8: Documentation & Reporting

**Duration:** 8-11 hours  
**Priority:** MEDIUM  
**Status:** Partial

### 8.1 Architecture Documentation

#### Step 1: Create Architecture Diagram
- Use draw.io, Lucidchart, or similar
- Show all components (GKE, VM, Cloud Functions)
- Indicate data flow
- Highlight networking

#### Step 2: Document Component Interactions
- Service-to-service communication
- Database connections
- Cloud Function invocations
- Load balancer routing

### 8.2 Deployment Documentation

#### Step 1: Create Deployment Guide
- Step-by-step instructions
- Prerequisites
- Troubleshooting guide
- Rollback procedures

#### Step 2: Update README.md
- Add GCP deployment section
- Include Cloud Function setup
- Add performance testing guide

### 8.3 Performance Test Documentation

#### Step 1: Document Test Design
- Test scenarios
- Parameters
- Independent/dependent variables

#### Step 2: Create Visualizations
- Response time charts
- Throughput graphs
- Resource utilization charts
- Error rate graphs

#### Step 3: Write Performance Analysis
- Observed results
- Reasoning and explanations
- Metrics interpretation
- Bottleneck identification

### 8.4 Cost Analysis Documentation

#### Step 1: Document Actual Costs
- Cost breakdown table
- Actual vs. estimated comparison
- Cost optimization measures

#### Step 2: Budget Compliance Report
- Demonstrate compliance with $300 budget
- Explain any cost overruns (if any)

**Deliverables:**
- ✅ Architecture diagram
- ✅ Deployment guide
- ✅ Performance test documentation
- ✅ Cost analysis document
- ✅ Updated README.md

---

## Phase 9: Final Testing & Validation

**Duration:** 3-5 hours  
**Priority:** HIGH  
**Status:** Not Started

### 9.1 End-to-End Testing

#### Step 1: Test All Features
- [ ] User registration
- [ ] User authentication
- [ ] Account creation
- [ ] Account details viewing
- [ ] Transaction processing
- [ ] Loan application (Cloud Function)
- [ ] ATM location search (Cloud Function)

#### Step 2: Verify HPA Scaling
```bash
# Generate load and observe scaling
# Verify pods scale up/down correctly
kubectl get hpa -n martianbank -w
```

#### Step 3: Test Under Load
- Run performance tests
- Verify system stability
- Check error rates

### 9.2 System Validation

#### Step 1: Requirements Checklist
- [x] Containerized workloads on Kubernetes (GKE)
- [x] Scalable deployment (HPA)
- [x] Virtual Machines (MongoDB VM)
- [ ] Serverless Functions (Loan, ATM Locator) - **PENDING**
- [ ] Performance testing (Locust) - **PENDING**
- [ ] Cost within budget - **PENDING**

#### Step 2: Create Validation Report
- Document all requirements met
- Note any deviations
- Create validation checklist

**Deliverables:**
- ✅ End-to-end test results
- ✅ Feature verification checklist
- ✅ System validation report

---

## Phase 10: Demo Video & Presentation Prep

**Duration:** 5-7 hours  
**Priority:** HIGH  
**Status:** Not Started

### 10.1 Demo Video Creation

#### Step 1: Plan Video Script (2 minutes max)
- **0:00-0:30:** Architecture overview
- **0:30-1:00:** Deployment demonstration
- **1:00-1:30:** Application features
- **1:30-2:00:** Performance testing

#### Step 2: Record Screen Capture
- Show GCP Console
- Demonstrate application features
- Show performance metrics
- Display cost breakdown

#### Step 3: Edit and Finalize
- Edit video
- Add captions if needed
- Upload to YouTube or hosting platform

### 10.2 Presentation Preparation

#### Step 1: Create Presentation Slides
- Architecture overview
- Design decisions
- Deployment process
- Performance results
- Cost analysis
- Lessons learned

#### Step 2: Prepare Talking Points
- Practice presentation
- Prepare Q&A responses

**Deliverables:**
- ✅ Demo video (2 minutes max)
- ✅ Presentation slides
- ✅ Presentation notes

---

## Quick Reference Commands

### Cloud Functions
```bash
# Deploy function
gcloud functions deploy <function-name> --gen2 --runtime=python311 --region=us-central1 --trigger-http

# Get function URL
gcloud functions describe <function-name> --gen2 --region=us-central1 --format="value(serviceConfig.uri)"

# View logs
gcloud functions logs read <function-name> --gen2 --region=us-central1
```

### Performance Testing
```bash
# Run Locust test
locust -f <test-file>.py --host=http://136.119.54.74:8080 --users=50 --spawn-rate=5 --run-time=10m

# Monitor during test
watch kubectl get pods -n martianbank
watch kubectl get hpa -n martianbank
```

### Cost Management
```bash
# Stop VM to save costs
gcloud compute instances stop mongodb-vm --zone=us-central1-a

# Start VM
gcloud compute instances start mongodb-vm --zone=us-central1-a

# Check costs
# Use GCP Console > Billing
```

---

## Timeline Estimate

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 3: Cloud Functions | 8-10 hours | HIGH |
| Phase 6: Performance Testing | 10-14 hours | HIGH |
| Phase 7: Cost Monitoring | 3-5 hours | MEDIUM |
| Phase 8: Documentation | 8-11 hours | MEDIUM |
| Phase 9: Final Testing | 3-5 hours | HIGH |
| Phase 10: Demo Video | 5-7 hours | HIGH |
| **Total** | **37-52 hours** | |

---

## Risk Mitigation

### Potential Issues & Solutions

1. **Cloud Function Cold Starts**
   - **Issue:** High latency on first invocation
   - **Solution:** Use Cloud Functions Gen 2, optimize code

2. **Performance Test Failures**
   - **Issue:** Application crashes under load
   - **Solution:** Start with low load, gradually increase, monitor resources

3. **Cost Overruns**
   - **Issue:** Exceeding $300 budget
   - **Solution:** Set up billing alerts, monitor daily, stop resources when not in use

4. **Documentation Time**
   - **Issue:** Documentation taking too long
   - **Solution:** Focus on essential docs first, add details later

---

## Success Criteria

### Must Complete
- [ ] Cloud Functions deployed and functional
- [ ] Performance tests executed
- [ ] Performance results documented
- [ ] Cost within budget
- [ ] Demo video created
- [ ] All requirements met

### Nice to Have
- [ ] Cost optimization implemented
- [ ] Comprehensive documentation
- [ ] Advanced monitoring dashboards

---

**Last Updated:** December 5, 2025  
**Document Version:** 1.0

