# Martian Bank - Remaining Steps Guide

**Date:** December 5, 2025  
**Project:** CMPE 48A Term Project - Martian Bank GCP Deployment  
**Status:** Phase 3 & Phase 5 Complete - Remaining Phases 6-10

---

## Overview

This guide provides detailed, step-by-step instructions for completing the remaining phases of the Martian Bank GCP deployment project. The project is currently at **70% completion**, with performance testing and documentation as the primary remaining tasks.

**Estimated Time to Complete:** 25-37 hours  
**Priority Order:** Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10

**Completed Phases:**
- ✅ Phase 1: Initial GKE Setup
- ✅ Phase 2: MongoDB VM Configuration  
- ✅ Phase 3: Cloud Functions Development (NEW)
- ✅ Phase 4: Application Deployment
- ✅ Phase 5: HPA and Load Balancer Configuration

---

## Phase 3: Cloud Functions Development ✅ COMPLETE

**Duration:** 8-10 hours  
**Priority:** HIGH (Required for full functionality)  
**Status:** ✅ COMPLETED on December 5, 2025

### Summary

Successfully deployed three Cloud Functions to replace containerized microservices:

1. **loan-request** (Python 3.11)
   - URL: https://loan-request-gcb4q3froa-uc.a.run.app
   - Entry Point: `process_loan_request`
   - Features: FormData support, MongoDB integration, 10-field validation

2. **loan-history** (Python 3.11)
   - URL: https://loan-history-gcb4q3froa-uc.a.run.app
   - Entry Point: `get_loan_history`
   - Features: Email-based history retrieval, formatted response

3. **atm-locator-service** (Node.js 20)
   - URL: https://atm-locator-service-gcb4q3froa-uc.a.run.app
   - Entry Point: `atmLocator`
   - Features: Random ATM selection (4 max), filter support

### Key Achievements
- ✅ Created VPC Connector (loan-connector) for MongoDB access
- ✅ Updated NGINX configuration with Cloud Function URLs
- ✅ Fixed FormData compatibility issues
- ✅ Fixed response format mismatches
- ✅ All endpoints tested and working in production

### Infrastructure
- **VPC Connector:** loan-connector (10.8.0.0/28, us-central1)
- **MongoDB:** 10.128.0.2:27017 (Private VM)
- **NGINX Image:** gcr.io/cmpe48a-term-project/martianbank-nginx:latest

**For detailed information, see:** `docs/PHASE3_COMPLETION_REPORT.md`

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
    'VITE_ATM_URL': 'http://136.119.54.74:8080/api/atm',  # Now routes to Cloud Function
    'VITE_TRANSFER_URL': 'http://136.119.54.74:8080/api/transaction',
    'VITE_LOAN_URL': 'http://136.119.54.74:8080/api/loan',  # Now routes to Cloud Function
    'VITE_LOAN_HISTORY_URL': 'http://136.119.54.74:8080/api/loanhistory',  # Cloud Function
}
```

**Note:** All URLs now point to the NGINX load balancer which routes to appropriate backends (GKE services or Cloud Functions).

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
# Install Locust (if not already installed)
pip install locust

# Test individual scripts against GCP endpoints
locust -f account_locust.py --host=http://136.119.54.74:8080
locust -f loan_locust.py --host=http://136.119.54.74:8080
locust -f atm_locust.py --host=http://136.119.54.74:8080

# Important: Update loan_locust.py to use /api/loanhistory endpoint
# Important: Update atm_locust.py to handle 4 ATM limit
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
- **Cloud Function metrics (NEW):**
  - Invocation count
  - Cold start frequency and latency
  - Warm response times
  - Error rates
  - Active instances
  - Memory usage
- Database connection pool usage
- VPC Connector throughput

**Commands:**
```bash
# Monitor pods during test
watch kubectl get pods -n martianbank

# Monitor HPA
watch kubectl get hpa -n martianbank

# Check pod metrics
kubectl top pods -n martianbank

# View Cloud Function metrics
# In GCP Console: Cloud Functions > Select function > Metrics tab

# View Cloud Function logs
gcloud functions logs read loan-request --gen2 --region=us-central1 --limit=50
gcloud functions logs read loan-history --gen2 --region=us-central1 --limit=50
gcloud functions logs read atm-locator-service --gen2 --region=us-central1 --limit=50
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
- [x] User registration
- [x] User authentication
- [x] Account creation
- [x] Account details viewing
- [x] Transaction processing
- [x] Loan application (Cloud Function) - **TESTED & WORKING**
- [x] Loan history (Cloud Function) - **TESTED & WORKING**
- [x] ATM location search (Cloud Function) - **TESTED & WORKING**

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

#### Step 2: Requirements Checklist
- [x] Containerized workloads on Kubernetes (GKE)
- [x] Scalable deployment (HPA)
- [x] Virtual Machines (MongoDB VM)
- [x] Serverless Functions (Loan, ATM Locator) - **✅ COMPLETE**
- [ ] Performance testing (Locust) - **PENDING**
- [ ] Cost within budget - **PENDING VALIDATION**

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

### Cloud Functions (DEPLOYED)
```bash
# Redeploy function (if changes made)
cd cloud-functions/<function-directory>
gcloud functions deploy <function-name> --gen2 --runtime=python311/nodejs20 \
  --region=us-central1 --source=. --entry-point=<entry-point> \
  --trigger-http --allow-unauthenticated --vpc-connector=loan-connector \
  --set-env-vars="DB_URL=mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin"

# Get function URL
gcloud functions describe <function-name> --gen2 --region=us-central1 --format="value(serviceConfig.uri)"

# View logs
gcloud functions logs read <function-name> --gen2 --region=us-central1 --limit=50

# Deployed Functions:
# - loan-request (https://loan-request-gcb4q3froa-uc.a.run.app)
# - loan-history (https://loan-history-gcb4q3froa-uc.a.run.app)
# - atm-locator-service (https://atm-locator-service-gcb4q3froa-uc.a.run.app)
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

| Phase | Duration | Priority | Status |
|-------|----------|----------|--------|
| ~~Phase 3: Cloud Functions~~ | ~~8-10 hours~~ | ~~HIGH~~ | ✅ **COMPLETE** |
| Phase 6: Performance Testing | 10-14 hours | HIGH | ⏳ Next |
| Phase 7: Cost Monitoring | 3-5 hours | MEDIUM | Pending |
| Phase 8: Documentation | 8-11 hours | MEDIUM | Pending |
| Phase 9: Final Testing | 3-5 hours | HIGH | Pending |
| Phase 10: Demo Video | 5-7 hours | HIGH | Pending |
| **Remaining** | **29-42 hours** | | **30% Left** |

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
- [x] Cloud Functions deployed and functional - **✅ COMPLETE**
- [ ] Performance tests executed - **NEXT PRIORITY**
- [ ] Performance results documented
- [ ] Cost within budget (validate)
- [ ] Demo video created
- [ ] All requirements met

### Nice to Have
- [ ] Cost optimization implemented
- [ ] Comprehensive documentation
- [ ] Advanced monitoring dashboards

---

**Last Updated:** December 5, 2025  
**Document Version:** 1.0

