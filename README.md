# MARTIAN BANK

<br />
 
MartianBank is a microservices demo application that simulates an app to allow customers to access and manage their bank accounts, perform financial transactions, locate ATMs, and apply for loans. It is built using [React](https://react.dev/),[ Node.js](https://nodejs.org/en/about), [Python](https://flask.palletsprojects.com/en/2.3.x/) and is packaged in [Docker](https://www.docker.com/) containers.  

<br />

# Highlights

- Micro Services Architecture  ​
- Helm based configurable deployments options​ (eg switching between HTTP and GRPC)​
- Docker, Kind and EKS based easy installations​
- Swagger APIs and comprehensive documentation​
- Performance tests and load generation capabilities​
- Integration with other opensource projects like APIClarity

<br />


# MARTIAN BANK

MartianBank is a microservices demo application that simulates a banking platform where customers can manage accounts, perform transactions, locate ATMs, and apply for loans. It is built using [React](https://react.dev/), [Node.js](https://nodejs.org/en/about), [Python](https://flask.palletsprojects.com/en/2.3.x/), and is packaged in [Docker](https://www.docker.com/) containers.

## Highlights

- Microservices Architecture
- Helm-based configurable deployment (HTTP/gRPC)
- GCP/GKE deployment with MongoDB on VM
- Performance/load testing with Locust

---

## Application Design

The Martian Bank UI is built with [React](https://react.dev/) and [Redux Toolkit](https://redux-toolkit.js.org/). NGINX acts as a reverse proxy for UI and backend services. There are 6 microservices: 2 (customer-auth, atm-locator) in Node.js, the rest in Python (Flask). The dashboard service communicates with accounts, transactions, and loan microservices via [gRPC](https://grpc.io/) or HTTP (configurable at deployment).


---

## Deployment Guide: GCP/GKE Setup

This guide explains how to deploy MartianBank on Google Cloud Platform using Google Kubernetes Engine (GKE) and a MongoDB VM. For troubleshooting and advanced details, see the docs/ folder.

## Prerequisites

Before installing MartianBank, make sure **all prerequisites below are fully satisfied**. Skipping any of these steps may result in failed deployments, pods stuck in `CrashLoopBackOff`, or LoadBalancer services remaining in `Pending` state.

---

### 1. GCP Account with Billing Enabled

MartianBank requires Google Cloud resources such as **GKE clusters**, **Compute Engine VMs**, and **LoadBalancer services**, all of which require an active billing account.

**Steps:**

1. Create or select a project in Google Cloud Console.
2. Link a billing account to the project.
3. Enable the following APIs:
   - Kubernetes Engine API
   - Compute Engine API
   - Cloud Resource Manager API

**Verify:**

```bash
gcloud projects list
gcloud config get-value project
```

---

### 2. Install and Authenticate `gcloud` CLI

The `gcloud` CLI is required to create GKE clusters, VM instances, and authenticate Docker to push images to GCR.

**Install:**

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Authenticate and set project:**

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**Verify:**

```bash
gcloud version
```

---

### 3. Install Docker

Docker is required to build and push container images for all microservices.

Install Docker Desktop:
[https://www.docker.com/get-started/](https://www.docker.com/get-started/)

Authenticate Docker with GCR:

```bash
gcloud auth configure-docker
```

Verify:

```bash
docker version
```

---

### 4. Install `kubectl`

`kubectl` is the Kubernetes command-line tool used to manage clusters, pods, and services.

**Install:**

```bash
gcloud components install kubectl
```

After creating your GKE cluster:

```bash
gcloud container clusters get-credentials martianbank-cluster \
  --zone=us-central1-a
```

Verify:

```bash
kubectl get nodes
```

---

### 5. Install Helm

MartianBank is deployed entirely using Helm charts. Helm v3 or later is required.

**Install:**

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Verify:**

```bash
helm version
```

---

# Deployment Steps

---

### 1. MongoDB VM Setup

1. **Create a VM** (Ubuntu 22.04 LTS, e2-small, no external IP, allow TCP:27017 from GKE):
  ```bash
  gcloud compute instances create mongodb-vm \
    --zone=us-central1-a \
    --machine-type=e2-small \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=40GB
  ```
2. **SSH into the VM and install MongoDB:**
  ```bash
  gcloud compute ssh mongodb-vm --zone=us-central1-a
  # Follow the steps in docs/MONGODB_VM_SETUP.md to install and secure MongoDB
  ```
3. **Configure MongoDB:**
  - Bind to `0.0.0.0` in `/etc/mongod.conf`
  - Create admin user and enable authentication
  - Note the internal IP (e.g., 10.128.0.2) and password
  - Open firewall for GKE nodes (see setup guide)

---

### 2. Build and Push Docker Images

1. **Set your GCP project:**
  ```bash
  export PROJECT_ID=$(gcloud config get-value project)
  ```
2. **Configure Docker for GCR:**
  ```bash
  gcloud auth configure-docker
  ```
3. **Build and push images:**
  ```bash
  docker build -t gcr.io/$PROJECT_ID/martianbank-ui:latest ./ui
  docker push gcr.io/$PROJECT_ID/martianbank-ui:latest
  # Repeat for customer-auth, accounts, transactions, dashboard, nginx
  ```

---

### 3. GKE Cluster Setup

1. **Create GKE cluster:**
  ```bash
  gcloud container clusters create martianbank-cluster \
    --zone=us-central1-a \
    --num-nodes=3 \
    --machine-type=e2-medium
  gcloud container clusters get-credentials martianbank-cluster --zone=us-central1-a
  ```
2. **Create namespace:**
  ```bash
  kubectl create namespace martianbank
  ```

---

### 4. Configure Secrets and ConfigMap

1. **Set variables:**
  ```bash
  export MONGODB_IP="10.128.0.2"  # Your VM's internal IP
  export MONGODB_PASSWORD="YOUR_MONGODB_PASSWORD"
  export JWT_SECRET=$(openssl rand -hex 32)
  ```
2. **Create ConfigMap:**
  ```bash
  kubectl create configmap configmap-martianbank \
    --from-literal=DB_URL="mongodb://root:${MONGODB_PASSWORD}@${MONGODB_IP}:27017/bank?authSource=admin" \
    --from-literal=JWT_SECRET="$JWT_SECRET" \
    --namespace=martianbank
  ```

---

### 5. Deploy with Helm

1. **Update `martianbank/values.yaml`** with:
  - Image repositories (point to GCR)
  - MongoDB connection string
  - Cloud Function URLs (if used)
2. **Install with Helm:**
  ```bash
  helm install martianbank ./martianbank \
    --namespace martianbank \
    --set SERVICE_PROTOCOL=http \
    --set DB_URL="mongodb://root:${MONGODB_PASSWORD}@${MONGODB_IP}:27017/bank?authSource=admin" \
    --set imageRegistry="gcr.io/$PROJECT_ID" \
    --set mongodb.enabled=false \
    --set nginx.enabled=true
  ```

---

### 6. Expose Application via Load Balancer

1. **Wait for NGINX service external IP:**
  ```bash
  kubectl get service nginx -n martianbank -w
  # When EXTERNAL-IP is assigned, access http://EXTERNAL_IP:8080
  ```

---

### 7. Configure Horizontal Pod Autoscaler (HPA)

> HPAs are configured manually after deployment. Only `transactions` and `customer-auth` services have HPA enabled.

1. **Install metrics server (if not already):**
  ```bash
  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
  kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=90s
  ```
2. **Create HPA for transactions:**
  ```bash
  kubectl autoscale deployment transactions -n martianbank --min=1 --max=3 --cpu=50%
  ```
3. **Create HPA for customer-auth:**
  ```bash
  kubectl autoscale deployment customer-auth -n martianbank --min=2 --max=2 --cpu=50%
  ```
4. **Verify HPAs:**
  ```bash
  kubectl get hpa -n martianbank
  kubectl describe hpa transactions -n martianbank
  kubectl describe hpa customer-auth -n martianbank
  ```

---

### 8. Access the Application

Once the NGINX service has an external IP, open `http://EXTERNAL_IP:8080` in your browser.

---

## Uninstalling MartianBank

1. **Uninstall with Helm:**
  ```bash
  helm uninstall martianbank -n martianbank
  ```
2. **Delete remaining resources (if needed):**
  ```bash
  kubectl delete all --all --namespace martianbank
  ```

---

## Troubleshooting

- Check pod status: `kubectl get pods -n martianbank`
- View logs: `kubectl logs <pod-name> -n martianbank`
- Describe pod: `kubectl describe pod <pod-name> -n martianbank`
- Test MongoDB connectivity from pod:
  ```bash
  kubectl run -it --rm mongo-test --image=mongo:latest --restart=Never --namespace=martianbank -- mongosh "mongodb://root:PASSWORD@10.128.0.2:27017/admin?authSource=admin"
  ```

---

## Performance Testing

1. **Update Locust URLs in `performance_locust/api_urls.py`**
2. **Run Locust tests:**
  ```bash
  cd performance_locust
  locust -f loan_locust.py --host=http://LOAD_BALANCER_IP
  ```

---

## License

This project is licensed under the MIT License.

Before installing MartianBank, you need to have Helm installed on your local machine.

-  Follow the official Helm installation guide based on your operating system: [Helm Installation Guide](https://helm.sh/docs/intro/install/)


**Step 4: Clone the MartianBank GitHub Repository**

1.  Open your terminal or command prompt.  

2.  Clone the MartianBank GitHub repository and navigate to the downloaded directory as mentioned in the previous tutorial.
```bash
git clone https://github.com/cisco-open/martian-bank-demo.git
cd martian-bank-demo
```

**Step 5: Install MartianBank using Helm**

Now that you have Minikube running and Helm installed, you can proceed with installing MartianBank on your Minikube cluster.

1.  To install MartianBank, use the Helm command:
```bash
helm install martianbank martianbank
```

Wait for the installation to complete. Helm will deploy the necessary components to your Minikube cluster.

**Step 6: Use Minikube Tunnel**

After installing MartianBank on your Minikube cluster, you may encounter that the command `kubectl get service` displays the services with an "external IP" in the "pending" state. This happens because Minikube does not natively support LoadBalancer type services with external IPs. However, you can use the `minikube tunnel` command to enable external access to LoadBalancer services.
  
To make the LoadBalancer type service accessible via an external IP in Minikube, you can use the `minikube tunnel` command. This command sets up a network route to expose the LoadBalancer's IP externally. Here's how to use it: Now, to make the LoadBalancer accessible from an external IP, run the following command in a **_new terminal_**:
```bash
minikube tunnel
```

The `minikube tunnel` command will create a network route to expose the LoadBalancer service to an external IP address. The external IP should no longer be in the "pending" state after running this command.

**Step 7: Access the MartianBank App**
  
After running `minikube tunnel`, the LoadBalancer's external IP should be available. You can get the IP by running:
```bash
kubectl get service
```
Look for the external IP in the output (for nginx pod). Copy the IP address and paste it into your browser's address bar. You should be able to access the MartianBank app.

**Step 8: Stop Minikube Tunnel**
Remember that the `minikube tunnel` command will continue running in your terminal until you stop it manually. When you're done testing the app, you can stop the tunnel by pressing `Ctrl + C` in the terminal where the `minikube tunnel` command is running.

That's it! Using `minikube tunnel`, you can expose LoadBalancer services in Minikube and access them via external IP addresses for testing and development.

  
**Step 9: Uninstall MartianBank**
If you want to uninstall MartianBank from your Minikube cluster, follow the same uninstallation steps mentioned in the previous tutorial:
```bash
helm uninstall martianbank
kubectl delete all --all --namespace default
```

That's it! You now have MartianBank installed and running on your Minikube cluster. Minikube provides an easy way to test and develop applications locally on a Kubernetes cluster. Happy testing with MartianBank on your Minikube setup!

<br />

##  3. Installation on Kind Cluster

**`Warning:`**  _Kind Cluster, by default, does not support the LoadBalancer type service with external IPs [[Load balancer external-ip pending · Issue #411 · kubernetes-sigs/kind (github.com)](https://github.com/kubernetes-sigs/kind/issues/411)]. This means that if you want to access services using an external IP in the Kind cluster, you will need to use an alternative approach. If you does not know how to resolove it, please follow the minikube or docker desktop kubernetes tutorials for installation setup._
  
Setting up MartianBank on a KIND (Kubernetes in Docker) cluster involves a few additional steps compared to a regular Kubernetes cluster. KIND allows you to create a lightweight Kubernetes cluster inside Docker containers, which is ideal for testing and development purposes. Here's how you can set up MartianBank on a KIND cluster:
  
**Step 1: Install KIND and Docker**
If you haven't already installed KIND and Docker, you need to do that first. Follow the official installation guides for [KIND](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) and [Docker](https://docs.docker.com/get-docker/) based on your operating system.
  
**Step 2: Create a KIND Cluster**

1.  Open your terminal or command prompt.

2.  Create a KIND cluster by running the following command:
```bash
kind create cluster --name martianbank
```

This will create a new KIND cluster named "martianbank" with a single Kubernetes node.
  
**Step 3: Configure Kubectl**
  
The KIND cluster should now be running, but your `kubectl` is not automatically configured to communicate with the cluster. You need to set the context for your `kubectl` to use the KIND cluster.

1.  Run the following command to set the `kubectl` context to the new KIND cluster:
```bash
kubectl cluster-info --context kind-martianbank
```

**Step 4: Install MartianBank using Helm**

Now that your KIND cluster is set up and Helm is installed, you can proceed with installing MartianBank.

1.  Clone the MartianBank GitHub repository and navigate to the downloaded directory as mentioned in the previous tutorial.
  
2.  Install MartianBank using the Helm command:
```bash
helm install martianbank martianbank
``` 

**Step 5: Access MartianBank App**
After the installation is complete, you can access the MartianBank app just like before. Find the IP address of the running MartianBank service using `kubectl get service` and access it in your browser (previous tutorial).


**Step 6: Uninstall MartianBank**
If you want to uninstall MartianBank from the KIND cluster, follow the same uninstallation steps mentioned in the previous tutorial:
```bash
helm uninstall martianbank
kubectl delete all --all --namespace default
```

That's it! You now have MartianBank installed and running on your KIND cluster. Remember that KIND clusters are ephemeral and will be destroyed once you delete them. You can always create a new cluster with the same name or a different one using `kind create cluster` if needed. Happy testing with MartianBank on your KIND cluster.

<br />  

## 4.  Installation on AWS EKS cluster

**Step 1: Create an EKS cluster on AWS:**

1. Install AWS CLI tool and configure it (pass in access key, secret key, region, and it creates ~/.aws/config and ~/.aws/credentials files).
```shell
aws configure
```

2. Install eksctl tool
```shell
brew tap weaveworks/tap; brew install weaveworks/tap/eksctl
```

3. Install IAM authenticator
```shell
brew install aws-iam-authenticator
```

4. Create a cluster.yaml file anywhere on your system.
```yaml
apiVersion: eksctl.io/v1alpha5 
kind: ClusterConfig 
metadata: 
  name: <cluster-name> 
  region: us-east-1 
vpc: 
  cidr: "172.20.0.0/16" ## Can change this value 
  nat: 
   gateway: Single 
  clusterEndpoints: 
   publicAccess: true 
   privateAccess: true 
nodeGroups: 
  - name: ng-1 
    minSize: 2 
    maxSize: 2 
    instancesDistribution: 
      maxPrice: 0.093 
      instanceTypes: ["t3a.large", "t3.large"] 
      onDemandBaseCapacity: 0 
      onDemandPercentageAboveBaseCapacity: 50 
      spotInstancePools: 2 
    ssh: 
     publicKeyPath: <path> 
```

5.  Create an EKS cluster using this command (takes ~20 minutes)
```shell
eksctl create cluster -f cluster.yaml
```

**Step 2: Install MartianBank using Helm**

Now that your EKS cluster is set up, you can proceed with installing MartianBank.

1.  Go to your cloned repository and install MartianBank using the Helm command:
```shell
helm install martianbank martianbank
```

By default loan, transaction and accounts microservices will run with http protocol. To switch to gRPC type the following command:
```bash
helm install martianbank martianbank --set SERVICE_PROTOCOL=grpc
```

Additionally, you can flip between mongoDB local and mongoDB Atlas (cloud database instance). To switch to mongoDB Atlas, use the following flag:
```bash
helm install martianbank martianbank --set "mongodb.enabled=true"
```

By default, we use NGINX for reverse-proxy. If you want to deploy without NGINX, use this flag:
```bash
helm install martianbank martianbank --set "nginx.enabled=false"
```

2.  Verify that all pods are running using this command:
```shell
kubectl get pods
```

**Step 3: Access MartianBank App**

After the installation is complete, you can access the MartianBank app by finding the IP address of the running MartianBank service using `kubectl get service` and access it in your browser.


**Step 4: Uninstall MartianBank**

If you want to uninstall MartianBank from the EKS cluster, follow these uninstallation steps:
```shell
helm uninstall martianbank
kubectl delete all --all --namespace default
```
  
<br />

## 5. Local Installation

**Option 1: Running on localhost**

1. Clone the MartianBank GitHub repository and navigate to the downloaded directory.
```bash
git clone https://github.com/cisco-open/martian-bank-demo.git
cd martian-bank-demo
```

2. Install mongodb locally and run it. Follow the steps here: https://www.mongodb.com/docs/manual/installation/

3. Before you start with the MartianBank installation, ensure that you have `.env` files setup inside all the microservices. You need to create a `.env` file under these folders: `./customer-auth`, `./atm-locator`, `./dashboard`, `./accounts`, `./loan`, `./transactions`. Each `.env` file should look like this:
```yaml
DB_URL="your-database-connection-url"
```

4. To run all the microservices and UI:  
```bash
cd scripts
bash run_local.sh
```

Fire up `http://localhost:3000` to access the Martian Bank App.

5. To stop all the microservices:
```bash
cd scripts
bash stop_local.sh
```

<br />

# Roadmap

- Images for background, coin, card, and map.
- Swagger docs for remaining endpoints
- Blog posts and videos to support contributors
- End-to-end and unit tests
- Injecting secrets securely
- https and certificates support

<br />

#  Contributing
Pull requests and bug reports are welcome. For larger changes please create an Issue in GitHub first to discuss your proposed changes and possible implications.

More more details please see the [Contribution guidelines for this project](CONTRIBUTING.md)

<br />

#  License

[BSD 3-Clause License](https://opensource.org/license/bsd-3-clause/)

