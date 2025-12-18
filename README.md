# MARTIAN BANK

MartianBank is a microservices demo application that simulates a banking platform where customers can manage accounts, perform transactions, locate ATMs, and apply for loans. It is built using **React**, **Node.js**, **Python (Flask)**, and packaged in **Docker** containers. The system is deployed on **Google Cloud Platform** using **GKE (Google Kubernetes Engine)** and **Cloud Functions (Gen 2)** with a shared MongoDB backend.

---

## Highlights

* Microservices architecture
* Helm-based configurable deployments (HTTP / gRPC)
* GKE for core services, Cloud Functions for serverless components
* Secure MongoDB VM accessed via private networking
* Swagger APIs and documentation
* Performance/load testing with Locust
* Real-world debugging and failure handling documented

---

## Application Architecture

* **UI (React)**: User-facing web application
* **NGINX**: Reverse proxy and single entry point
* **GKE Microservices**:

  * `customer-auth` (Node.js)
  * `dashboard` (Python)
  * `accounts` (Python)
  * `transactions` (Python)
* **Cloud Functions (Gen 2)**:

  * `atmLocator` (Node.js)
  * `process_loan_request` (Python)
  * `get_loan_history` (Python)
* **MongoDB**: Single MongoDB instance running on a private Compute Engine VM

> GKE pods and Cloud Functions both access MongoDB via internal VPC networking.

---

## Deployment Guide: GCP / GKE + Cloud Functions

This guide explains how to deploy the **entire MartianBank system** end-to-end.

---

## Prerequisites

### 1. GCP Project & Billing

* Create/select a GCP project
* Enable billing
* Enable APIs:

```bash
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

Verify:

```bash
gcloud config get-value project
```

---

### 2. Install Tooling

```bash
# gcloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# kubectl
gcloud components install kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Verify:

```bash
gcloud version
kubectl version --client
helm version
```

---

### 3. Docker

Install Docker Desktop and authenticate:

```bash
gcloud auth configure-docker
```

---

## Step 1 – MongoDB VM Setup

### 1.1 Create VM

```bash
gcloud compute instances create mongodb-vm \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=40GB
```

### 1.2 Install MongoDB

```bash
gcloud compute ssh mongodb-vm --zone=us-central1-a

sudo apt update
sudo apt install -y curl gnupg ca-certificates

curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] \
https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | \
sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt update
sudo apt install -y mongodb-org
sudo systemctl enable mongod
sudo systemctl start mongod
```

### 1.3 Configure MongoDB

Edit `/etc/mongod.conf`:

```yaml
net:
  bindIp: 0.0.0.0
security:
  authorization: enabled
```

Restart:

```bash
sudo systemctl restart mongod
```

Create admin user:

```bash
mongosh
use admin

db.createUser({
  user: "root",
  pwd: "STRONG_PASSWORD",
  roles: [{ role: "root", db: "admin" }]
})
```

Get internal IP:

```bash
gcloud compute instances describe mongodb-vm \
  --zone us-central1-a \
  --format="get(networkInterfaces[0].networkIP)"
```

---

## Step 2 – Firewall Rules (Critical)

GKE **pods** use a different CIDR than nodes. Both must be allowed.

```bash
gcloud compute instances add-tags mongodb-vm \
  --zone=us-central1-a \
  --tags=mongodb

# Allow Node + Pod CIDR
gcloud compute firewall-rules create allow-mongodb-from-gke \
  --network=default \
  --direction=INGRESS \
  --rules=tcp:27017 \
  --source-ranges=10.128.0.0/20,10.12.0.0/14 \
  --target-tags=mongodb
```

---

## Step 3 – Build & Push Docker Images

```bash
PROJECT_ID=$(gcloud config get-value project)

docker build -t gcr.io/$PROJECT_ID/martianbank-ui:latest ./ui
docker push gcr.io/$PROJECT_ID/martianbank-ui:latest

docker build -t gcr.io/$PROJECT_ID/martianbank-nginx:latest ./nginx
docker push gcr.io/$PROJECT_ID/martianbank-nginx:latest

docker build -t gcr.io/$PROJECT_ID/martianbank-customer-auth:latest -f customer-auth/Dockerfile .
docker push gcr.io/$PROJECT_ID/martianbank-customer-auth:latest

docker build -t gcr.io/$PROJECT_ID/martianbank-dashboard:latest -f dashboard/Dockerfile .
docker push gcr.io/$PROJECT_ID/martianbank-dashboard:latest

docker build -t gcr.io/$PROJECT_ID/martianbank-accounts:latest -f accounts/Dockerfile .
docker push gcr.io/$PROJECT_ID/martianbank-accounts:latest

docker build -t gcr.io/$PROJECT_ID/martianbank-transactions:latest -f transactions/Dockerfile .
docker push gcr.io/$PROJECT_ID/martianbank-transactions:latest
```

---

## Step 4 – GKE Cluster

```bash
gcloud container clusters create martianbank-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --disk-size=40

gcloud container clusters get-credentials martianbank-cluster --zone us-central1-a
kubectl create namespace martianbank
```

---

## Step 5 – Deploy GKE Services with Helm

```bash
MONGODB_IP="10.128.0.2"
MONGODB_PASSWORD="STRONG_PASSWORD"
JWT_SECRET=$(openssl rand -hex 32)

DB_URL="mongodb://root:${MONGODB_PASSWORD}@${MONGODB_IP}:27017/bank?authSource=admin"

helm install martianbank ./martianbank \
  -n martianbank --create-namespace \
  --set imageRegistry="gcr.io/$PROJECT_ID" \
  --set mongodb.enabled=false \
  --set nginx.enabled=true \
  --set DB_URL="$DB_URL" \
  --set JWT_SECRET="$JWT_SECRET"
```

---

## Step 6 – Deploy Cloud Functions (Gen 2)

### ATM Locator (Node.js)

```bash
cd cloud-functions/atm-locator

gcloud functions deploy atmLocator \
  --gen2 \
  --runtime=nodejs20 \
  --region=us-central1 \
  --entry-point=atmLocator \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars DB_URL="$DB_URL"
```

### Loan Functions (Python)

```bash
cd cloud-functions/loan

gcloud functions deploy process_loan_request \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --entry-point=process_loan_request \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars DB_URL="$DB_URL"


gcloud functions deploy get_loan_history \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --entry-point=get_loan_history \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars DB_URL="$DB_URL"
```

Resolve URLs:

```bash
PROCESS_LOAN_URL=$(gcloud functions describe process_loan_request --gen2 --region=us-central1 --format="value(serviceConfig.uri)")
LOAN_HISTORY_URL=$(gcloud functions describe get_loan_history --gen2 --region=us-central1 --format="value(serviceConfig.uri)")
ATM_LOCATOR_URL=$(gcloud functions describe atmLocator --gen2 --region=us-central1 --format="value(serviceConfig.uri)")
```

Upgrade Helm:

```bash
helm upgrade martianbank ./martianbank \
  -n martianbank \
  --set cloudFunctions.loanRequestURL="$PROCESS_LOAN_URL" \
  --set cloudFunctions.loanHistoryURL="$LOAN_HISTORY_URL" \
  --set cloudFunctions.atmLocatorURL="$ATM_LOCATOR_URL"
```

---

## Access Application

```bash
kubectl get service nginx -n martianbank -w
```

Open:

```
http://EXTERNAL_IP:8080
```

---

## Troubleshooting

* `ImagePullBackOff` → image name mismatch
* `CrashLoopBackOff` → MongoDB not reachable (firewall / CIDR)
* `502 Bad Gateway` → backend pods down or Cloud Function URL missing

---

## Uninstall

```bash
helm uninstall martianbank -n martianbank
kubectl delete namespace martianbank
```

---

## License

BSD 3-Clause License
