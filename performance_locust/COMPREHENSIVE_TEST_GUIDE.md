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

## Running the Tests

### **Prerequisites**
```bash
# Install Locust
pip install locust faker

# Verify connectivity
curl http://136.119.54.74:8080/api/users/
```

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