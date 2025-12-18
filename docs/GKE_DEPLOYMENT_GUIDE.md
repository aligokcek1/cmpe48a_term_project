# GKE Deployment Guide - Phase 4 & 5

## Prerequisites Checklist

- [x] GKE cluster created and connected
- [x] MongoDB VM set up and accessible
- [x] `kubectl` configured (`kubectl get nodes` works)
- [x] `docker` installed locally
- [x] `gcloud` CLI authenticated
- [x] MongoDB connection string ready

## Step 1: Get Your Project ID and Configure Docker

```bash
# Get your project ID
export PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"

# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker
```

## Step 2: Get MongoDB VM Internal IP

You'll need this for the ConfigMap. Get it from one of these methods:

**Option A: From GCP Console**
- Go to Compute Engine > VM instances
- Find your MongoDB VM
- Copy the Internal IP (starts with 10.x.x.x)

**Option B: From Command Line**
```bash
# Replace VM_NAME and ZONE with your values
gcloud compute instances describe <VM_NAME> --zone=<ZONE> --format='get(networkInterfaces[0].networkIP)'
```

**Save this IP - you'll need it!**

## Step 3: Build and Push Docker Images

I'll create a script for this. For now, here are the manual commands:

### 3.1 Build and Push UI Image

```bash
cd /Users/aligokcek1/Documents/GitHub/cmpe48a_term_project

# Build UI image
docker build -t gcr.io/$PROJECT_ID/martianbank-ui:latest ./ui

# Push to GCR
docker push gcr.io/$PROJECT_ID/martianbank-ui:latest
```

### 3.2 Build and Push Customer-Auth Image

```bash
docker build -t gcr.io/$PROJECT_ID/martianbank-customer-auth:latest ./customer-auth
docker push gcr.io/$PROJECT_ID/martianbank-customer-auth:latest
```

### 3.3 Build and Push Accounts Image

```bash
docker build -t gcr.io/$PROJECT_ID/martianbank-accounts:latest .
docker push gcr.io/$PROJECT_ID/martianbank-accounts:latest
```

**Note**: Accounts Dockerfile expects to be built from root directory (it copies protobufs/)

### 3.4 Build and Push Transactions Image

```bash
docker build -t gcr.io/$PROJECT_ID/martianbank-transactions:latest .
docker push gcr.io/$PROJECT_ID/martianbank-transactions:latest
```

### 3.5 Build and Push Dashboard Image

```bash
docker build -t gcr.io/$PROJECT_ID/martianbank-dashboard:latest .
docker push gcr.io/$PROJECT_ID/martianbank-dashboard:latest
```

### 3.6 Build and Push NGINX Image

```bash
docker build -t gcr.io/$PROJECT_ID/martianbank-nginx:latest ./nginx
docker push gcr.io/$PROJECT_ID/martianbank-nginx:latest
```

### 3.7 Verify Images Are Pushed

```bash
gcloud container images list --repository=gcr.io/$PROJECT_ID
```

You should see all your images listed.

## Step 4: Update Helm Chart Configuration

### 4.1 Update ConfigMap Template

We need to update the ConfigMap with your MongoDB connection string. Let me create an updated version.

### 4.2 Update values.yaml

Update `martianbank/values.yaml` with:
- Image repositories pointing to GCR
- MongoDB connection string
- Enable HPA

## Step 5: Deploy to GKE

### 5.1 Create ConfigMap with MongoDB Connection

First, let's create the ConfigMap manually with your MongoDB connection string:

```bash
# Replace these values:
# - MONGODB_IP: Your MongoDB VM internal IP
# - MONGODB_PASSWORD: Your MongoDB root password
# - JWT_SECRET: Any random string for JWT signing

kubectl create configmap configmap-martianbank \
  --from-literal=DB_URL="mongodb://root:MONGODB_PASSWORD@MONGODB_IP:27017/bank?authSource=admin" \
  --from-literal=JWT_SECRET="your-random-jwt-secret-key-here" \
  --namespace=martianbank
```

**Example:**
```bash
kubectl create configmap configmap-martianbank \
  --from-literal=DB_URL="mongodb://root:MyPass123@10.128.0.2:27017/bank?authSource=admin" \
  --from-literal=JWT_SECRET="my-super-secret-jwt-key-12345" \
  --namespace=martianbank
```

### 5.2 Deploy with Helm

```bash
cd /Users/aligokcek1/Documents/GitHub/cmpe48a_term_project

# Install Helm chart
helm install martianbank ./martianbank \
  --namespace martianbank \
  --set SERVICE_PROTOCOL=http \
  --set DB_URL="mongodb://root:MONGODB_PASSWORD@MONGODB_IP:27017/bank?authSource=admin"
```

### 5.3 Check Deployment Status

```bash
# Check all pods
kubectl get pods -n martianbank

# Watch pods until all are Running
kubectl get pods -n martianbank -w

# Check services
kubectl get services -n martianbank

# Check logs if any pod is failing
kubectl logs <pod-name> -n martianbank
```

## Step 6: Configure Load Balancer

### 6.1 Update NGINX Service to LoadBalancer

The NGINX service needs to be exposed externally. Let's check the current service configuration and update it:

```bash
# Check current service
kubectl get service nginx -n martianbank -o yaml

# Patch service to LoadBalancer type
kubectl patch service nginx -n martianbank -p '{"spec":{"type":"LoadBalancer"}}'
```

### 6.2 Get External IP

```bash
# Wait for external IP assignment (may take 1-2 minutes)
kubectl get service nginx -n martianbank -w

# Once assigned, get the IP
kubectl get service nginx -n martianbank
```

The EXTERNAL-IP column will show your public IP address.

### 6.3 Access Application

Open your browser and go to:
```
http://EXTERNAL_IP:8080
```

## Step 7: Configure HPA (Horizontal Pod Autoscaler) - Manual Configuration

**Important:** HPAs are configured manually using `kubectl` commands, not via Helm charts. This allows for fine-grained control over scaling behavior. Only transactions and customer-auth services have HPA enabled.

### 7.1 Enable Metrics Server

```bash
# Check if metrics server exists
kubectl get deployment metrics-server -n kube-system

# If not exists, install it (required for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Wait for metrics server to be ready
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=90s
```

### 7.2 Create HPA for Transactions Service

```bash
# Create HPA (min: 1, max: 3, CPU target: 50%)
kubectl autoscale deployment transactions -n martianbank \
  --min=1 \
  --max=3 \
  --cpu=50%

# Verify HPA creation
kubectl get hpa transactions -n martianbank
```

### 7.3 Create HPA for Customer-Auth Service

```bash
# Create HPA (fixed at 2 replicas, CPU target: 50%)
kubectl autoscale deployment customer-auth -n martianbank \
  --min=2 \
  --max=2 \
  --cpu=50%

# Verify HPA creation
kubectl get hpa customer-auth -n martianbank
```

### 7.4 Update Existing HPA (if needed)

If HPAs already exist and you need to modify them:

```bash
# Update transactions HPA max replicas
kubectl patch hpa transactions -n martianbank -p '{"spec":{"maxReplicas":3}}'

# Update transactions HPA min replicas
kubectl patch hpa transactions -n martianbank -p '{"spec":{"minReplicas":1}}'

# Update CPU threshold to 50%
kubectl patch hpa transactions -n martianbank -p '{"spec":{"metrics":[{"type":"Resource","resource":{"name":"cpu","target":{"type":"Utilization","averageUtilization":50}}}]}}'

# Update customer-auth HPA (min and max to 2)
kubectl patch hpa customer-auth -n martianbank -p '{"spec":{"minReplicas":2,"maxReplicas":2}}'
```

### 7.5 Verify All HPAs

```bash
# List all HPAs
kubectl get hpa -n martianbank

# View detailed HPA information
kubectl describe hpa transactions -n martianbank
kubectl describe hpa customer-auth -n martianbank
```

**Note:** Other services (UI, Dashboard, Accounts, NGINX) run without HPA at fixed replica counts (1 replica each). When you use `kubectl patch hpa`, you're modifying the live Kubernetes resource in the cluster's etcd database. This does NOT modify any files in your codebase.

## Troubleshooting

### Images Not Pulling

```bash
# Check if GKE can access GCR
kubectl run test-pod --image=gcr.io/$PROJECT_ID/martianbank-ui:latest --rm -it --restart=Never --namespace=martianbank

# If permission denied, ensure GKE has proper IAM permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')-compute@developer.gserviceaccount.com \
  --role=roles/storage.objectViewer
```

### Pods Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n martianbank

# Check logs
kubectl logs <pod-name> -n martianbank

# Common issues:
# - Image pull errors → Check image name and GCR permissions
# - Database connection errors → Check MongoDB VM IP and firewall rules
# - ConfigMap not found → Ensure ConfigMap is created in correct namespace
```

### Database Connection Issues

```bash
# Test MongoDB connectivity from a pod
kubectl run -it --rm debug --image=busybox --restart=Never --namespace=martianbank -- nslookup MONGODB_VM_IP

# Test MongoDB connection from a pod
kubectl run -it --rm mongo-test --image=mongo:latest --restart=Never --namespace=martianbank -- mongosh "mongodb://root:PASSWORD@MONGODB_IP:27017/admin?authSource=admin"
```

### Service Not Getting External IP

```bash
# Check service status
kubectl describe service nginx -n martianbank

# Check for LoadBalancer events
kubectl get events -n martianbank --sort-by='.lastTimestamp'
```

## Next Steps

After successful deployment:

1. ✅ Test all application features
2. ✅ Verify HPA is working (generate some load)
3. ✅ Proceed to Phase 6: Performance Testing with Locust
4. ✅ Update Locust test URLs to point to your Load Balancer IP

## Quick Reference Commands

```bash
# Set project
export PROJECT_ID=$(gcloud config get-value project)

# Get MongoDB VM IP
gcloud compute instances describe <VM_NAME> --zone=<ZONE> --format='get(networkInterfaces[0].networkIP)'

# Build and push image (template)
docker build -t gcr.io/$PROJECT_ID/martianbank-SERVICE:latest ./SERVICE
docker push gcr.io/$PROJECT_ID/martianbank-SERVICE:latest

# Check pods
kubectl get pods -n martianbank

# Check services
kubectl get services -n martianbank

# Get external IP
kubectl get service nginx -n martianbank

# View logs
kubectl logs -f <pod-name> -n martianbank

# Delete everything (if needed)
helm uninstall martianbank -n martianbank
kubectl delete namespace martianbank
```

---

**Ready to proceed?** Let me know when you've completed the image builds and we'll move to deployment!

