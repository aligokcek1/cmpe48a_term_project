# MongoDB VM Setup Guide

## Prerequisites
- ✅ VM created and SSH access established
- VM should be running Ubuntu 22.04 LTS
- You should be logged into the VM via SSH

## Step-by-Step Installation

### Step 1: Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install MongoDB Community Edition

#### 2.1 Import MongoDB GPG Key
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
```

#### 2.2 Add MongoDB Repository
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

#### 2.3 Install MongoDB
```bash
sudo apt update
sudo apt install -y mongodb-org
```

#### 2.4 Prevent Automatic Updates (Optional but Recommended)
```bash
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-database hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-mongosh hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
```

### Step 3: Start and Enable MongoDB
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
sudo systemctl status mongod
```

Verify MongoDB is running - you should see "active (running)" in the status output.

### Step 4: Configure MongoDB for Network Access

#### 4.1 Edit MongoDB Configuration
```bash
sudo nano /etc/mongod.conf
```

#### 4.2 Update Network Configuration
Find the `net:` section and update it to:
```yaml
net:
  port: 27017
  bindIp: 0.0.0.0  # Listen on all interfaces (or use VM's internal IP)
```

**Note**: `bindIp: 0.0.0.0` allows MongoDB to accept connections from any IP. For production, you might want to restrict this to specific IPs, but for now this will work with GKE.

#### 4.3 Save and Restart MongoDB
```bash
# Save the file (Ctrl+O, Enter, Ctrl+X in nano)
sudo systemctl restart mongod
sudo systemctl status mongod
```

### Step 5: Set Up Authentication

#### 5.1 Connect to MongoDB (No Auth Yet)
```bash
mongosh
```

#### 5.2 Create Admin User
In the MongoDB shell, run:
```javascript
use admin
db.createUser({
  user: "root",
  pwd: "your-secure-password-here",  // CHANGE THIS!
  roles: [ { role: "root", db: "admin" } ]
})
```

**⚠️ IMPORTANT**: Replace `your-secure-password-here` with a strong password. Save this password - you'll need it for the connection string!

#### 5.3 Create Application Database and User
```javascript
use bank
db.createUser({
  user: "bankuser",
  pwd: "bank-password-here",  // CHANGE THIS!
  roles: [ { role: "readWrite", db: "bank" } ]
})
```

#### 5.4 Exit MongoDB Shell
```javascript
exit
```

#### 5.5 Enable Authentication in MongoDB Config
```bash
sudo nano /etc/mongod.conf
```

Find the `security:` section (or add it if it doesn't exist) and add:
```yaml
security:
  authorization: enabled
```

Save and restart:
```bash
sudo systemctl restart mongod
```

#### 5.6 Test Authentication
```bash
mongosh -u root -p --authenticationDatabase admin
# Enter the root password when prompted
```

If you can connect, authentication is working!

### Step 6: Configure Firewall Rules

#### 6.1 Get VM's Internal IP Address
```bash
hostname -I
# Note the internal IP (usually starts with 10.x.x.x)
```

#### 6.2 Exit SSH and Configure GCP Firewall (from your local machine)
```bash
exit  # Exit from VM SSH
```

On your local machine, create a firewall rule to allow MongoDB access from GKE:

```bash
# Get your GKE cluster network (you'll need this when you create the cluster)
# For now, create a rule that allows from your GKE cluster's network
# Replace <GKE_NETWORK> with your cluster's network name

gcloud compute firewall-rules create allow-mongodb-from-gke \
  --allow tcp:27017 \
  --source-ranges 10.0.0.0/8 \
  --target-tags mongodb-server \
  --description "Allow MongoDB access from GKE cluster"
```

**Alternative**: If you want to test from your local machine first:
```bash
gcloud compute firewall-rules create allow-mongodb-from-local \
  --allow tcp:27017 \
  --source-ranges 0.0.0.0/0 \
  --target-tags mongodb-server \
  --description "Allow MongoDB access for testing (restrict later)"
```

**⚠️ Security Note**: The second rule allows access from anywhere. Use it only for testing, then restrict it to your GKE cluster's IP range.

#### 6.3 Tag Your VM (if not already tagged)
```bash
# Get VM name and zone
gcloud compute instances list

# Add tag to VM
gcloud compute instances add-tags <VM_NAME> \
  --tags mongodb-server \
  --zone <ZONE>
```

### Step 7: Get VM's External IP (for Connection String)

```bash
# From your local machine
gcloud compute instances describe <VM_NAME> --zone <ZONE> --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Or check in GCP Console: Compute Engine > VM instances > Your VM > External IP

### Step 8: Test Connection from Local Machine

#### 8.1 Test Connection (Optional - for verification)
From your local machine, test the connection:

```bash
# Install MongoDB client locally (if not installed)
# macOS: brew install mongodb-community
# Linux: sudo apt install mongodb-community-clients

# Test connection
mongosh "mongodb://root:your-password@<VM_EXTERNAL_IP>:27017/admin?authSource=admin"
```

If connection succeeds, MongoDB is accessible!

### Step 9: Document Connection Strings

Create a connection string document. You'll need these formats:

#### For GKE Services (Internal IP - Recommended):
```
mongodb://root:your-password@<VM_INTERNAL_IP>:27017/bank?authSource=admin
```

#### For Cloud Functions (External IP):
```
mongodb://root:your-password@<VM_EXTERNAL_IP>:27017/bank?authSource=admin
```

#### For Application User (Alternative):
```
mongodb://bankuser:bank-password@<VM_INTERNAL_IP>:27017/bank?authSource=bank
```

**Get Internal IP:**
```bash
# From VM
hostname -I

# Or from local machine
gcloud compute instances describe <VM_NAME> --zone <ZONE> --format='get(networkInterfaces[0].networkIP)'
```

### Step 10: Create Database Initialization Script (Optional)

Create a script to initialize your database with the required collections:

```bash
# On the VM
nano /home/ubuntu/init-db.js
```

Add this content:
```javascript
// Connect to MongoDB
use bank

// Create collections (they'll be created when first document is inserted)
// Collections will be created automatically by the application:
// - accounts
// - transactions
// - loans
// - users (managed by customer-auth service)
// - atms (seeded by atm-locator service)

print("Database 'bank' is ready for use");
```

Run it:
```bash
mongosh -u root -p --authenticationDatabase admin < /home/ubuntu/init-db.js
```

## Connection String Format

Save this information for later use in your ConfigMap:

```
mongodb://root:PASSWORD@VM_INTERNAL_IP:27017/bank?authSource=admin
```

**Example:**
```
mongodb://root:MySecurePass123@10.128.0.2:27017/bank?authSource=admin
```

## Security Checklist

- [x] MongoDB installed and running
- [x] Authentication enabled
- [x] Root user created
- [x] Application user created (optional)
- [x] Network binding configured (0.0.0.0)
- [x] Firewall rules configured
- [x] Connection tested
- [ ] **TODO**: Restrict firewall to GKE cluster IP range only (after cluster creation)
- [ ] **TODO**: Consider using SSL/TLS for production (optional for this project)

## Troubleshooting

### MongoDB Won't Start
```bash
# Check logs
sudo journalctl -u mongod -n 50

# Check if port is in use
sudo netstat -tulpn | grep 27017
```

### Can't Connect from Outside
- Verify firewall rules: `gcloud compute firewall-rules list`
- Check VM tags: `gcloud compute instances describe <VM_NAME> --zone <ZONE>`
- Verify MongoDB is listening: `sudo netstat -tulpn | grep 27017`
- Check MongoDB config: `cat /etc/mongod.conf | grep bindIp`

### Authentication Fails
- Verify user exists: `mongosh -u root -p --authenticationDatabase admin`
- Check user roles: In mongosh, run `db.getUsers()`
- Verify security config: `cat /etc/mongod.conf | grep authorization`

## Next Steps

1. ✅ MongoDB is now installed and configured
2. **Next**: Note down your connection string
3. **Next**: Proceed to Phase 3 (Cloud Functions) or Phase 4 (GKE Setup)
4. **Remember**: You'll need the VM's internal IP for GKE services and external IP for Cloud Functions

## Important Notes

- **Internal IP**: Use this for GKE services (faster, no egress charges)
- **External IP**: Use this for Cloud Functions (if needed)
- **Password**: Keep your MongoDB password secure - you'll need it for ConfigMap
- **Firewall**: After creating GKE cluster, restrict firewall to cluster's IP range

---

**Save this information:**
- VM Name: _______________
- Zone: _______________
- Internal IP: _______________
- External IP: _______________
- Root Password: _______________
- Connection String: _______________

