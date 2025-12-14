# Martian Bank - Comprehensive Performance Testing Guide

## Overview

This comprehensive performance testing suite evaluates the entire Martian Bank system under realistic workloads. The test simulates real user behavior across all system components.

## Test Components Covered

### ✅ **1. Customer Authentication Service (GKE)**
- User registration
- Login/logout
- Profile updates

### ✅ **2. Account Management Service (GKE)**
- Account creation (Checking, Savings, Money Market, Investment)
- View all accounts
- Get account details

### ✅ **3. Transaction Service (GKE)**
- Internal transfers (between own accounts)
- External transfers (Zelle-style)
- Transaction history

### ✅ **4. Loan Service (Cloud Function)**
- Loan application submission
- Loan history retrieval

### ✅ **5. ATM Locator Service (Cloud Function)**
- ATM location search

### ✅ **6. NGINX Load Balancer**
- Request routing
- Proxy performance

### ✅ **7. MongoDB VM**
- Database read/write performance
- Connection pooling

---

## Test File Overview

### `comprehensive_system_test.py` (Main Test)

**Purpose:** Simulates complete, realistic user journeys through the entire banking system.

**User Journey:**
1. **Registration** → User creates account in auth service
2. **Login** → User authenticates
3. **Account Creation** → User creates checking and savings accounts
4. **Account Viewing** → User checks balances and details (high frequency)
5. **Transactions** → User makes internal/external transfers
6. **Transaction History** → User reviews past transactions
7. **ATM Search** → User finds nearby ATMs
8. **Loan Application** → User applies for loans
9. **Loan History** → User checks loan status
10. **Profile Updates** → User modifies profile (occasional)
11. **Logout/Re-login** → User session management

**Task Weights (Simulating Realistic Behavior):**
```
view_account_details:      20  (Most frequent - checking balance)
view_all_accounts:         15  (High frequency)
check_transaction_history: 12  (Regular activity)
internal_transfer:         10  (Medium frequency)
search_atm_locations:       5  (Occasional)
check_loan_history:         4  (Low-medium)
apply_for_loan:             3  (Rare)
update_profile:             2  (Rare)
logout_and_login:           1  (Very rare)
```

**User Personas:**
- **Casual Banking User** (70%): Longer wait times, occasional usage
- **Heavy Transaction User** (30%): Shorter wait times, frequent transfers

---

## Test Scenarios

### **Scenario 1: Baseline (Light Load)**
- **Users:** 10
- **Spawn Rate:** 2 users/second
- **Duration:** 5 minutes
- **Purpose:** Establish performance baseline with minimal load
- **Expected Behavior:** All requests succeed, low latency, no scaling

### **Scenario 2: Normal Operations**
- **Users:** 50
- **Spawn Rate:** 5 users/second
- **Duration:** 5 minutes
- **Purpose:** Simulate typical business hours
- **Expected Behavior:** Stable performance, possible minimal HPA scaling

### **Scenario 3: Peak Hours (High Load)**
- **Users:** 100
- **Spawn Rate:** 10 users/second
- **Duration:** 5 minutes
- **Purpose:** Simulate peak banking activity (lunch hour, payday)
- **Expected Behavior:** HPA scaling triggers, increased latency acceptable

### **Scenario 4: Stress Test**
- **Users:** 200+
- **Spawn Rate:** 20 users/second
- **Duration:** 5 minutes
- **Purpose:** Identify system breaking point and maximum capacity
- **Expected Behavior:** Aggressive scaling, some errors acceptable, system recovers

---

## Running the Tests

### **Prerequisites**
```bash
# Install Locust
pip install locust faker

# Verify connectivity
curl http://136.119.54.74:8080/api/users/
```

### **Method 1: Automated Script (Recommended)**

**On Windows (PowerShell):**
```powershell
cd performance_locust
.\run_comprehensive_tests.ps1
```

**On Linux/Mac (Bash):**
```bash
cd performance_locust
chmod +x run_comprehensive_tests.sh
./run_comprehensive_tests.sh
```

### **Method 2: Manual Execution**

**Single Test Run:**
```bash
cd performance_locust

# Run comprehensive test
locust -f comprehensive_system_test.py \
  --host=http://136.119.54.74:8080 \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless \
  --html=results/test_report.html \
  --csv=results/test_data
```

**Interactive Mode (with Web UI):**
```bash
locust -f comprehensive_system_test.py --host=http://136.119.54.74:8080

# Open browser to: http://localhost:8089
# Configure users, spawn rate, and duration in UI
```

### **Method 3: Component-Specific Tests**

```bash
# Test authentication only
locust -f auth_locust.py --host=http://136.119.54.74:8080 --users=30 --spawn-rate=3 --run-time=5m

# Test account service only
locust -f account_locust.py --host=http://136.119.54.74:8080 --users=30 --spawn-rate=3 --run-time=5m

# Test transactions only
locust -f transaction_locust.py --host=http://136.119.54.74:8080 --users=30 --spawn-rate=3 --run-time=5m

# Test loan cloud functions only
locust -f loan_locust.py --host=http://136.119.54.74:8080 --users=20 --spawn-rate=2 --run-time=5m

# Test ATM cloud function only
locust -f atm_locust.py --host=http://136.119.54.74:8080 --users=20 --spawn-rate=2 --run-time=5m
```

---

## Monitoring During Tests

### **Terminal 1: Pod Monitoring**
```bash
watch -n 2 kubectl get pods -n martianbank
```

### **Terminal 2: HPA Monitoring**
```bash
watch -n 5 kubectl get hpa -n martianbank
```

### **Terminal 3: Resource Usage**
```bash
watch -n 5 kubectl top pods -n martianbank
```

### **Terminal 4: Cloud Function Logs**
```bash
# Loan service
gcloud functions logs read loan-request --gen2 --region=us-central1 --limit=50

# ATM service
gcloud functions logs read atm-locator-service --gen2 --region=us-central1 --limit=50
```

### **GCP Console Dashboards**
1. **GKE Cluster:** Kubernetes Engine → Clusters → martianbank-cluster → Monitoring
2. **Cloud Functions:** Cloud Functions → Select function → Metrics tab
3. **VM:** Compute Engine → VM instances → mongodb-vm → Monitoring
4. **Load Balancer:** Network Services → Load balancing

---

## Metrics to Collect

### **From Locust Reports**
- Total requests
- Failures (count and %)
- Response times:
  - Minimum
  - Maximum
  - Average
  - Median (50th percentile)
  - 95th percentile
  - 99th percentile
- Requests per second (RPS)
- Error distribution by endpoint

### **From GKE (Kubernetes)**
- Pod count over time (HPA scaling behavior)
- CPU utilization per pod
- Memory utilization per pod
- Pod restart count
- Network I/O

### **From Cloud Functions**
- Invocation count
- Cold start frequency and latency
- Warm invocation latency
- Error rate
- Active instances
- Memory usage

### **From MongoDB VM**
- CPU utilization
- Memory usage
- Disk I/O (IOPS, throughput)
- Network traffic
- Active connections

### **From NGINX Load Balancer**
- Request rate
- Response codes (2xx, 4xx, 5xx)
- Latency
- Connections

---

## Expected Results

### **Success Criteria**

| Metric | Baseline | Normal | Peak | Stress |
|--------|----------|--------|------|--------|
| **Success Rate** | >99% | >98% | >95% | >90% |
| **Avg Response Time** | <200ms | <500ms | <1s | <2s |
| **95th Percentile** | <500ms | <1s | <2s | <5s |
| **HPA Scaling** | No scaling | 0-2 replicas | 2-5 replicas | Max replicas |
| **Error Rate** | <1% | <2% | <5% | <10% |

### **Cloud Function Performance**
- **Cold Start:** <3 seconds (acceptable for first invocation)
- **Warm Response:** <500ms (Python), <200ms (Node.js)
- **Scaling:** Should auto-scale based on concurrency

### **Database Performance**
- **CPU:** Should stay <80% under peak load
- **Memory:** Stable, no OOM issues
- **Connections:** Should not exhaust connection pool

---

## Interpreting Results

### **HTML Report Analysis**

1. **Open Report:** `results/scenario1_baseline_TIMESTAMP.html`

2. **Check Statistics Tab:**
   - Green = Success
   - Red = Failures
   - Look for high failure % (indicates issues)

3. **Check Charts Tab:**
   - **Response Times:** Should be relatively flat, spikes indicate problems
   - **Users:** Shows ramp-up pattern
   - **RPS:** Should increase with users

4. **Check Failures Tab:**
   - Identify which endpoints are failing
   - Check error messages

### **CSV Data Analysis**

Import CSV into Excel/Google Sheets for detailed analysis:
- `*_stats.csv`: Request statistics
- `*_stats_history.csv`: Metrics over time
- `*_failures.csv`: Error details

### **Common Issues**

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| High 504 errors | Service timeout | Increase NGINX timeout, check pod logs |
| High 503 errors | Service unavailable | Check if pods are running, increase replicas |
| Increasing response times | Resource contention | Check CPU/memory, adjust HPA |
| Cold start spikes | Cloud Function cold starts | Expected, monitor warm latency |
| Connection errors | MongoDB connection pool | Check VM resources, increase pool size |

---

## Post-Test Analysis Checklist

- [ ] Review all Locust HTML reports
- [ ] Analyze CSV data for trends
- [ ] Screenshot GCP monitoring dashboards
- [ ] Document HPA scaling behavior
- [ ] Record Cloud Function metrics
- [ ] Note any errors or anomalies
- [ ] Compare results across scenarios
- [ ] Identify performance bottlenecks
- [ ] Document optimization recommendations

---

## Troubleshooting

### **Test Won't Start**
```bash
# Check Locust installation
pip install --upgrade locust faker

# Verify connectivity
curl -v http://136.119.54.74:8080/api/users/

# Check Python version (requires 3.7+)
python --version
```

### **High Error Rates**
```bash
# Check pod status
kubectl get pods -n martianbank

# Check pod logs
kubectl logs -n martianbank <pod-name>

# Check NGINX logs
kubectl logs -n martianbank -l app=nginx
```

### **Tests Timeout**
- Increase timeout in test files (already set to 60s)
- Check if services are responding
- Verify MongoDB VM is running

---

## Best Practices

1. **Start Small:** Always run baseline test first
2. **Monitor Continuously:** Keep GCP Console open during tests
3. **Wait Between Tests:** Allow 5-10 minutes between scenarios for pods to scale down
4. **Document Everything:** Take screenshots, note observations
5. **Save Results:** Archive all reports with timestamps
6. **Test Incrementally:** Don't jump straight to stress test
7. **Check Logs:** Review application logs after each test
8. **Cost Awareness:** Stop tests if costs spike unexpectedly

---

## Report Generation

After completing all tests, create a comprehensive performance report including:

1. **Executive Summary**
2. **Test Methodology**
3. **System Architecture**
4. **Test Scenarios**
5. **Results Analysis** (with charts and tables)
6. **Bottleneck Identification**
7. **Optimization Recommendations**
8. **Conclusion**

See `docs/PERFORMANCE_TEST_REPORT.md` template for guidance.

---

## Contact & Support

For issues or questions about performance testing:
- Review existing test files for examples
- Check GCP logs for errors
- Consult `docs/REMAINING_STEPS_GUIDE.md` for deployment details

---

**Last Updated:** December 13, 2025  
**Version:** 1.0
