# CMPE 48A Term Project - GCP Deployment Roadmap

## Executive Summary

This roadmap outlines the complete migration and deployment strategy for the Martian Bank application to Google Cloud Platform (GCP), transforming it into a cloud-native architecture that meets all term project requirements.

**Target Architecture:**
- **Containerized Core (GKE)**: Frontend UI, Accounts, Transactions, Dashboard, Customer-Auth services
- **Virtual Machine (Compute Engine)**: MongoDB database instance
- **Serverless (Cloud Functions)**: Loan and ATM Locator services
- **Load Balancing**: Global HTTP(S) Load Balancer
- **Auto-scaling**: Horizontal Pod Autoscaler (HPA) for backend services

---

## Phase 1: Pre-Deployment Setup & Planning

### 1.1 GCP Project Setup
**Duration:** 1-2 hours

**Tasks:**
- [ ] Create new GCP project (or use existing)
- [ ] Enable billing and verify $300 free trial credits
- [ ] Enable required APIs:
  - Kubernetes Engine API
  - Compute Engine API
  - Cloud Functions API
  - Cloud Build API
  - Container Registry API
  - Cloud Monitoring API
- [ ] Set up IAM roles and service accounts
- [ ] Configure project ID and region/zone preferences
- [ ] Install and configure `gcloud` CLI locally

**Deliverables:**
- GCP project created and configured
- Service account with appropriate permissions
- `gcloud` CLI authenticated

**Cost Impact:** $0 (setup only)

---

### 1.2 Codebase Analysis & Preparation
**Duration:** 2-3 hours

**Tasks:**
- [x] Analyze current microservices architecture
- [ ] Identify dependencies between services
- [ ] Document current database schema and collections
- [ ] Review Helm chart structure and templates
- [ ] Identify environment variables and configuration needs
- [ ] Review Locust test scripts and update endpoints

**Current Microservices:**
1. **UI** (React) - Frontend application
2. **Customer-Auth** (Node.js) - Authentication service
3. **Accounts** (Python/Flask) - Account management
4. **Transactions** (Python/Flask) - Transaction processing
5. **Dashboard** (Python/Flask) - Dashboard service
6. **Loan** (Python/Flask) - **→ Convert to Cloud Function**
7. **ATM-Locator** (Node.js/Express) - **→ Convert to Cloud Function**
8. **MongoDB** - **→ Deploy on Compute Engine VM**

**Deliverables:**
- Architecture documentation
- Dependency mapping diagram
- Configuration requirements list

---

## Phase 2: Database Migration to Compute Engine

### 2.1 MongoDB VM Setup
**Duration:** 2-3 hours

**Tasks:**
- [ ] Create Compute Engine VM instance:
  - Machine type: `e2-small` (0.5 vCPU, 2GB RAM)
  - OS: Ubuntu 22.04 LTS
  - Boot disk: 40GB Standard Persistent Disk
  - Firewall rules: Allow MongoDB port (27017) from GKE cluster only
- [ ] Install MongoDB on VM:
  - Install MongoDB Community Edition
  - Configure MongoDB for network access
  - Set up authentication (root user/password)
  - Configure firewall and security groups
- [ ] Create persistent data disk (if needed)
- [ ] Test MongoDB connectivity from local machine
- [ ] Document connection string format

**VM Configuration:**
```bash
# Example gcloud command
gcloud compute instances create mongodb-vm \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=40GB \
  --tags=mongodb-server
```

**Deliverables:**
- MongoDB VM running and accessible
- Connection string documented
- Security configuration verified

**Cost Impact:** ~$11.10/month

---

### 2.2 Database Migration & Testing
**Duration:** 1-2 hours

**Tasks:**
- [ ] Export existing database schema (if any test data exists)
- [ ] Create database initialization scripts
- [ ] Test database connectivity from all microservices
- [ ] Verify ATM data seeding works correctly
- [ ] Document database backup procedures

**Deliverables:**
- Database accessible from GKE cluster
- Test data loaded
- Connection strings updated in ConfigMap

---

## Phase 3: Cloud Functions Development

### 3.1 Loan Service Cloud Function
**Duration:** 4-5 hours

**Tasks:**
- [ ] Analyze current `loan/loan.py` implementation
- [ ] Create Cloud Function structure:
  ```
  cloud-functions/
    loan/
      main.py
      requirements.txt
      .env.yaml (for secrets)
  ```
- [ ] Convert Flask endpoints to Cloud Function HTTP handlers:
  - `/loan/request` → `process_loan_request(request)`
  - `/loan/history` → `get_loan_history(request)`
- [ ] Update MongoDB connection to use VM IP
- [ ] Handle CORS for Cloud Function
- [ ] Test locally using Functions Framework
- [ ] Deploy to GCP:
  ```bash
  gcloud functions deploy loan-service \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point process_loan_request \
    --memory 512MB \
    --timeout 60s
  ```
- [ ] Update UI and dashboard to use Cloud Function URL
- [ ] Test end-to-end loan application flow

**Key Changes:**
- Replace Flask `@app.route` with Cloud Function entry points
- Update MongoDB connection string to VM IP
- Handle HTTP request/response format for Cloud Functions
- Configure CORS headers

**Deliverables:**
- Loan Cloud Function deployed and tested
- Function URL documented
- Integration with frontend verified

**Cost Impact:** ~$0 (within free tier: 2M invocations/month)

---

### 3.2 ATM Locator Cloud Function
**Duration:** 4-5 hours

**Tasks:**
- [ ] Analyze current `atm-locator/server.js` implementation
- [ ] Create Cloud Function structure:
  ```
  cloud-functions/
    atm-locator/
      index.js
      package.json
      config/
        atm_data.json
  ```
- [ ] Convert Express routes to Cloud Function HTTP handlers:
  - `/api/atm` routes → Cloud Function handlers
- [ ] Update MongoDB connection to use VM IP
- [ ] Handle database seeding in Cloud Function initialization
- [ ] Test locally using Functions Framework
- [ ] Deploy to GCP:
  ```bash
  gcloud functions deploy atm-locator-service \
    --runtime nodejs18 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point handler \
    --memory 512MB \
    --timeout 60s
  ```
- [ ] Update UI to use Cloud Function URL
- [ ] Test ATM location search functionality

**Key Changes:**
- Convert Express app to Cloud Function format
- Move database seeding to Cloud Function initialization
- Update MongoDB connection to VM IP
- Handle CORS for Cloud Function

**Deliverables:**
- ATM Locator Cloud Function deployed and tested
- Function URL documented
- Integration with frontend verified

**Cost Impact:** ~$0 (within free tier)

---

## Phase 4: GKE Cluster Setup & Configuration

### 4.1 GKE Cluster Creation
**Duration:** 1-2 hours

**Tasks:**
- [ ] Create GKE cluster:
  - Cluster type: Zonal (to avoid management fees)
  - Zone: `us-central1-a` (or preferred zone)
  - Node pool: 3x `e2-medium` instances (2 vCPU, 4GB RAM)
  - Enable preemptible instances (optional, for cost savings)
  - Kubernetes version: Latest stable
- [ ] Configure cluster networking:
  - VPC network configuration
  - Subnet configuration
  - Firewall rules for MongoDB VM access
- [ ] Set up kubectl context:
  ```bash
  gcloud container clusters get-credentials <cluster-name> --zone <zone>
  ```
- [ ] Verify cluster connectivity
- [ ] Install Helm (if not already installed)

**Cluster Configuration:**
```bash
gcloud container clusters create martianbank-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=5 \
  --enable-autorepair \
  --enable-autoupgrade
```

**Deliverables:**
- GKE cluster running
- kubectl configured
- Network connectivity verified

**Cost Impact:** ~$139.20/month (3x e2-medium nodes)

---

### 4.2 Container Image Management
**Duration:** 2-3 hours

**Tasks:**
- [ ] Set up Container Registry or Artifact Registry
- [ ] Build and push Docker images for each microservice:
  - UI
  - Customer-Auth
  - Accounts
  - Transactions
  - Dashboard
- [ ] Update Helm chart image references:
  - Change from `ghcr.io/cisco-open/...` to `gcr.io/<project-id>/...`
- [ ] Test image pulls from GKE cluster
- [ ] Document image build and push process

**Build Commands:**
```bash
# For each service
docker build -t gcr.io/<project-id>/martianbank-ui:latest ./ui
docker push gcr.io/<project-id>/martianbank-ui:latest
```

**Deliverables:**
- All images pushed to GCR/Artifact Registry
- Helm charts updated with new image paths
- Build scripts documented

**Cost Impact:** ~$0 (storage costs minimal)

---

### 4.3 Helm Chart Updates for GKE
**Duration:** 3-4 hours

**Tasks:**
- [ ] Update `martianbank/values.yaml`:
  - Set `DB_URL` to MongoDB VM connection string
  - Update image repositories
  - Configure service types (LoadBalancer for ingress)
  - Enable HPA configuration
- [ ] Update `martianbank/templates/configmap.yaml`:
  - Add MongoDB VM connection string
  - Add Cloud Function URLs for Loan and ATM services
  - Configure JWT_SECRET
- [ ] Remove Loan and ATM-Locator deployments (now Cloud Functions)
- [ ] Update service configurations
- [ ] Configure resource limits and requests
- [ ] Test Helm chart rendering:
  ```bash
  helm template martianbank ./martianbank --debug
  ```

**Key Updates:**
- Remove `loan` and `atm-locator` deployments
- Update `DB_URL` in ConfigMap to VM IP
- Add Cloud Function URLs to ConfigMap
- Configure HPA for Accounts and Transactions services

**Deliverables:**
- Updated Helm charts
- ConfigMap with correct environment variables
- Chart tested and validated

---

## Phase 5: Deployment & Service Configuration

### 5.1 Initial Deployment
**Duration:** 2-3 hours

**Tasks:**
- [ ] Create namespace (optional):
  ```bash
  kubectl create namespace martianbank
  ```
- [ ] Create ConfigMap with MongoDB and Cloud Function URLs
- [ ] Deploy using Helm:
  ```bash
  helm install martianbank ./martianbank \
    --namespace martianbank \
    --set DB_URL="mongodb://root:password@<vm-ip>:27017" \
    --set SERVICE_PROTOCOL=http
  ```
- [ ] Verify all pods are running:
  ```bash
  kubectl get pods -n martianbank
  ```
- [ ] Check pod logs for errors
- [ ] Verify service connectivity

**Deliverables:**
- All services deployed and running
- Pods healthy
- Services communicating correctly

---

### 5.2 Load Balancer & Ingress Configuration
**Duration:** 2-3 hours

**Tasks:**
- [ ] Configure LoadBalancer service for NGINX:
  - Update service type to `LoadBalancer`
  - Configure external IP allocation
- [ ] Set up Ingress (alternative approach):
  - Create Ingress resource
  - Configure backend services
  - Set up SSL certificates (optional, for HTTPS)
- [ ] Wait for external IP assignment
- [ ] Update DNS (if applicable) or document IP address
- [ ] Test external access to application
- [ ] Configure firewall rules for Load Balancer

**Ingress Configuration:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: martianbank-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 8080
```

**Deliverables:**
- External IP assigned
- Application accessible via browser
- Load balancer configured

**Cost Impact:** ~$18.25/month (Load Balancer)

---

### 5.3 Horizontal Pod Autoscaler (HPA) Configuration
**Duration:** 2-3 hours

**Tasks:**
- [ ] Enable metrics server (if not already enabled):
  ```bash
  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
  ```
- [ ] Update HPA configuration in Helm chart:
  - Target: Accounts and Transactions services
  - Min replicas: 1
  - Max replicas: 5-10
  - CPU threshold: 70-80%
  - Memory threshold: 80% (optional)
- [ ] Deploy HPA:
  ```bash
  kubectl apply -f martianbank/templates/hpa.yaml
  ```
- [ ] Verify HPA is active:
  ```bash
  kubectl get hpa -n martianbank
  ```
- [ ] Test autoscaling with load generation
- [ ] Document HPA behavior and thresholds

**HPA Configuration:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: accounts-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: accounts
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Deliverables:**
- HPA configured and active
- Autoscaling tested and verified
- Documentation of scaling behavior

---

## Phase 6: Performance Testing & Optimization

### 6.1 Locust Test Updates
**Duration:** 3-4 hours

**Tasks:**
- [ ] Update `performance_locust/api_urls.py`:
  - Replace localhost URLs with GCP endpoints
  - Add Cloud Function URLs for Loan and ATM
  - Update Load Balancer IP/URL
- [ ] Review and update all Locust test files:
  - `account_locust.py`
  - `transaction_locust.py`
  - `loan_locust.py`
  - `atm_locust.py`
  - `auth_locust.py`
- [ ] Configure test parameters:
  - User count (ramp-up strategy)
  - Spawn rate
  - Test duration
  - Think time between requests
- [ ] Test Locust scripts locally against GCP endpoints
- [ ] Create test execution scripts

**Updated API URLs:**
```python
ApiUrls = {
    'VITE_ACCOUNTS_URL': 'http://<load-balancer-ip>/account',
    'VITE_USERS_URL': 'http://<load-balancer-ip>/api/users',
    'VITE_ATM_URL': 'https://<region>-<project-id>.cloudfunctions.net/atm-locator-service',
    'VITE_TRANSFER_URL': 'http://<load-balancer-ip>/transaction',
    'VITE_LOAN_URL': 'https://<region>-<project-id>.cloudfunctions.net/loan-service',
}
```

**Deliverables:**
- Updated Locust test scripts
- Test execution documentation
- Baseline performance metrics

---

### 6.2 Performance Test Execution
**Duration:** 4-6 hours

**Tasks:**
- [ ] Set up monitoring dashboards:
  - GCP Cloud Monitoring
  - Kubernetes metrics
  - Application metrics
- [ ] Design test scenarios:
  - **Scenario 1**: Low load (10 users, 5 min)
  - **Scenario 2**: Medium load (50 users, 10 min)
  - **Scenario 3**: High load (100 users, 15 min)
  - **Scenario 4**: Stress test (200+ users, 20 min)
- [ ] Execute tests and collect metrics:
  - Request latency (p50, p95, p99)
  - Throughput (requests/second)
  - Error rates
  - CPU/Memory utilization
  - Pod scaling events
- [ ] Document results:
  - Create charts and graphs
  - Analyze performance bottlenecks
  - Identify optimization opportunities
- [ ] Run multiple test iterations for statistical significance

**Metrics to Collect:**
- Response times (min, max, avg, percentiles)
- Requests per second (RPS)
- Error rates (4xx, 5xx)
- Pod count over time
- CPU/Memory usage per pod
- Database connection pool usage
- Cloud Function invocation metrics

**Deliverables:**
- Performance test results
- Visualizations (charts, graphs)
- Analysis report
- Optimization recommendations

---

### 6.3 Performance Optimization
**Duration:** 3-4 hours

**Tasks:**
- [ ] Analyze performance bottlenecks
- [ ] Optimize based on findings:
  - Adjust HPA thresholds
  - Tune resource requests/limits
  - Optimize database queries
  - Configure connection pooling
  - Enable caching (if applicable)
- [ ] Re-run performance tests
- [ ] Compare before/after metrics
- [ ] Document optimizations

**Deliverables:**
- Optimized configuration
- Performance improvement metrics
- Optimization documentation

---

## Phase 7: Cost Monitoring & Optimization

### 7.1 Cost Tracking Setup
**Duration:** 1-2 hours

**Tasks:**
- [ ] Set up GCP billing alerts:
  - Alert at $100
  - Alert at $200
  - Alert at $250
- [ ] Create cost breakdown dashboard
- [ ] Document expected costs per component
- [ ] Set up daily cost monitoring

**Cost Breakdown (Expected):**
- GKE Nodes (3x e2-medium): ~$139.20/month
- Database VM (e2-small): ~$11.10/month
- Load Balancer: ~$18.25/month
- Storage (Disks): ~$4.00/month
- Cloud Functions: ~$0 (free tier)
- **Total: ~$172.55/month**

**Deliverables:**
- Billing alerts configured
- Cost tracking dashboard
- Cost documentation

---

### 7.2 Cost Optimization Strategies
**Duration:** 2-3 hours

**Tasks:**
- [ ] Implement cost-saving measures:
  - Use preemptible nodes (if stable)
  - Stop VMs when not in use
  - Right-size instances based on actual usage
  - Clean up unused resources
- [ ] Create scripts for resource management:
  - Start/stop scripts for VM
  - Cluster scaling scripts
- [ ] Document cost optimization procedures

**Deliverables:**
- Cost optimization scripts
- Resource management procedures
- Updated cost estimates

---

## Phase 8: Documentation & Reporting

### 8.1 Architecture Documentation
**Duration:** 3-4 hours

**Tasks:**
- [ ] Create cloud architecture diagram:
  - Show all components
  - Indicate data flow
  - Highlight GKE, VM, and Cloud Functions
  - Show Load Balancer and networking
- [ ] Document component interactions
- [ ] Create deployment flowchart
- [ ] Document configuration details

**Deliverables:**
- Architecture diagram (using draw.io, Lucidchart, or similar)
- Component interaction documentation
- Network topology diagram

---

### 8.2 Deployment Documentation
**Duration:** 2-3 hours

**Tasks:**
- [ ] Create step-by-step deployment guide:
  - Prerequisites
  - GCP setup steps
  - Database VM setup
  - Cloud Functions deployment
  - GKE cluster setup
  - Application deployment
  - Verification steps
- [ ] Document troubleshooting guide
- [ ] Create README.md with deployment instructions
- [ ] Document rollback procedures

**Deliverables:**
- Complete deployment guide
- README.md updated
- Troubleshooting documentation

---

### 8.3 Performance Test Documentation
**Duration:** 2-3 hours

**Tasks:**
- [ ] Document Locust experiment design:
  - Test scenarios
  - Parameters and configurations
  - Independent/dependent variables
- [ ] Create performance results visualization:
  - Response time charts
  - Throughput graphs
  - Resource utilization charts
  - Error rate graphs
- [ ] Write performance analysis:
  - Observed results
  - Reasoning and explanations
  - Performance metrics interpretation
  - Bottleneck identification

**Deliverables:**
- Performance test design document
- Visualized results (charts/graphs)
- Performance analysis report

---

### 8.4 Cost Analysis Documentation
**Duration:** 1-2 hours

**Tasks:**
- [ ] Document actual costs vs. estimates
- [ ] Create cost breakdown table
- [ ] Explain cost optimization measures
- [ ] Demonstrate compliance with $300 budget
- [ ] Document cost monitoring procedures

**Deliverables:**
- Cost breakdown document
- Budget compliance report
- Cost optimization documentation

---

## Phase 9: Final Testing & Validation

### 9.1 End-to-End Testing
**Duration:** 2-3 hours

**Tasks:**
- [ ] Test all application features:
  - User registration and authentication
  - Account creation
  - Account details viewing
  - Transaction processing
  - Loan application (Cloud Function)
  - ATM location search (Cloud Function)
- [ ] Verify HPA scaling behavior
- [ ] Test under load
- [ ] Verify Cloud Function invocations
- [ ] Check database connectivity and data persistence

**Deliverables:**
- End-to-end test results
- Feature verification checklist
- Bug reports (if any)

---

### 9.2 System Validation
**Duration:** 1-2 hours

**Tasks:**
- [ ] Verify all requirements met:
  - ✅ Containerized workloads on Kubernetes (GKE)
  - ✅ Scalable deployment (HPA)
  - ✅ Virtual Machines (MongoDB VM)
  - ✅ Serverless Functions (Loan, ATM Locator)
  - ✅ Performance testing (Locust)
  - ✅ Cost within budget
- [ ] Create validation checklist
- [ ] Document any deviations or issues

**Deliverables:**
- Requirements validation checklist
- System validation report

---

## Phase 10: Demo Video & Presentation Prep

### 10.1 Demo Video Creation
**Duration:** 2-3 hours

**Tasks:**
- [ ] Plan video script (max 2 minutes):
  - Architecture overview (30s)
  - Deployment demonstration (30s)
  - Application features (30s)
  - Performance testing (30s)
- [ ] Record screen capture:
  - Show GCP console
  - Demonstrate application features
  - Show performance metrics
  - Display cost breakdown
- [ ] Edit and finalize video
- [ ] Upload to YouTube or hosting platform

**Deliverables:**
- Demo video (2 minutes max)
- Video script

---

### 10.2 Presentation Preparation
**Duration:** 3-4 hours

**Tasks:**
- [ ] Create presentation slides:
  - Architecture overview
  - Design decisions
  - Deployment process
  - Performance results
  - Cost analysis
  - Lessons learned
- [ ] Prepare talking points
- [ ] Practice presentation
- [ ] Prepare Q&A responses

**Deliverables:**
- Presentation slides
- Presentation notes

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Pre-Deployment Setup | 3-5 hours | 3-5 hours |
| Phase 2: Database Migration | 3-5 hours | 6-10 hours |
| Phase 3: Cloud Functions | 8-10 hours | 14-20 hours |
| Phase 4: GKE Setup | 6-9 hours | 20-29 hours |
| Phase 5: Deployment | 6-9 hours | 26-38 hours |
| Phase 6: Performance Testing | 10-14 hours | 36-52 hours |
| Phase 7: Cost Optimization | 3-5 hours | 39-57 hours |
| Phase 8: Documentation | 8-11 hours | 47-68 hours |
| Phase 9: Final Testing | 3-5 hours | 50-73 hours |
| Phase 10: Demo & Presentation | 5-7 hours | 55-80 hours |

**Total Estimated Time: 55-80 hours**

---

## Risk Mitigation

### Potential Risks & Mitigation Strategies

1. **Cost Overruns**
   - **Risk**: Exceeding $300 budget
   - **Mitigation**: Set up billing alerts, monitor daily, use preemptible nodes, stop resources when not in use

2. **Cloud Function Cold Starts**
   - **Risk**: High latency on first invocation
   - **Mitigation**: Use Cloud Functions Gen 2, implement warm-up strategies, optimize function code

3. **Database Connectivity Issues**
   - **Risk**: VM firewall blocking GKE cluster
   - **Mitigation**: Proper firewall configuration, VPC peering, test connectivity early

4. **HPA Not Scaling Properly**
   - **Risk**: Pods not scaling under load
   - **Mitigation**: Verify metrics server, test HPA thresholds, monitor scaling events

5. **Performance Test Failures**
   - **Risk**: Application crashes under load
   - **Mitigation**: Start with low load, gradually increase, monitor resources, optimize bottlenecks

6. **Image Build/Push Issues**
   - **Risk**: Docker images not building or pushing correctly
   - **Mitigation**: Test builds locally, verify registry permissions, use CI/CD if possible

---

## Success Criteria

### Technical Requirements ✅
- [ ] All microservices deployed on GKE
- [ ] MongoDB running on Compute Engine VM
- [ ] Loan service deployed as Cloud Function
- [ ] ATM Locator deployed as Cloud Function
- [ ] HPA configured and tested
- [ ] Load Balancer configured and accessible
- [ ] All services communicating correctly
- [ ] Application fully functional

### Performance Requirements ✅
- [ ] Performance tests executed with Locust
- [ ] Metrics collected (latency, throughput, errors)
- [ ] Results visualized and documented
- [ ] Performance analysis completed

### Cost Requirements ✅
- [ ] Total cost within $300 budget
- [ ] Cost breakdown documented
- [ ] Cost optimization measures implemented

### Documentation Requirements ✅
- [ ] Architecture diagram created
- [ ] Deployment guide written
- [ ] Performance test results documented
- [ ] Cost analysis completed
- [ ] README.md updated
- [ ] Demo video created (2 min max)

---

## Next Steps

1. **Immediate Actions:**
   - Set up GCP project and enable APIs
   - Review this roadmap with team member
   - Allocate time for each phase

2. **Week 1:**
   - Complete Phases 1-2 (Setup & Database)
   - Begin Phase 3 (Cloud Functions)

3. **Week 2:**
   - Complete Phase 3 (Cloud Functions)
   - Complete Phase 4 (GKE Setup)

4. **Week 3:**
   - Complete Phase 5 (Deployment)
   - Begin Phase 6 (Performance Testing)

5. **Week 4:**
   - Complete Phase 6 (Performance Testing)
   - Complete Phase 7 (Cost Optimization)

6. **Week 5:**
   - Complete Phases 8-9 (Documentation & Testing)
   - Begin Phase 10 (Demo Video)

7. **Final Week:**
   - Complete Phase 10 (Demo & Presentation)
   - Final review and submission

---

## Additional Resources

### GCP Documentation
- [GKE Quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstart)
- [Cloud Functions Python Guide](https://cloud.google.com/functions/docs/create-deploy-http-python)
- [Cloud Functions Node.js Guide](https://cloud.google.com/functions/docs/create-deploy-http-node)
- [Compute Engine VM Setup](https://cloud.google.com/compute/docs/instances/create-start-instance)
- [MongoDB on GCP](https://cloud.google.com/architecture/mongodb)

### Kubernetes & Helm
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Helm Documentation](https://helm.sh/docs/)

### Performance Testing
- [Locust Documentation](https://docs.locust.io/)
- [GCP Cloud Monitoring](https://cloud.google.com/monitoring)

---

## Notes

- **Budget Buffer**: Estimated cost is $172.55/month, leaving ~$127 buffer for unexpected costs
- **Preemptible Nodes**: Consider using preemptible nodes for GKE to reduce costs (~50% savings)
- **VM Management**: Stop MongoDB VM when not actively testing to save costs
- **Load Balancer**: Delete Load Balancer when not in use to avoid charges
- **Monitoring**: Set up comprehensive monitoring early to catch issues quickly
- **Backup Strategy**: Implement database backup procedures for MongoDB VM

---

**Last Updated:** [Current Date]
**Version:** 1.0
**Authors:** Ali Gökçek, Umut Şendağ

