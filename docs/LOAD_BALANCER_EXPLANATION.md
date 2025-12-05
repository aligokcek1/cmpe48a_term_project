# GCP Load Balancer - Multiple Services Explained

## Short Answer

**Yes!** If you expose each service directly with `type: LoadBalancer`, **each service gets its own Load Balancer** = **Multiple Load Balancers** = **Expensive!**

## Detailed Explanation

### Scenario 1: Each Service with LoadBalancer Type ❌ (Expensive)

If you configure each service like this:

```yaml
# accounts service
apiVersion: v1
kind: Service
metadata:
  name: accounts
spec:
  type: LoadBalancer  # Creates Load Balancer #1
  ports:
    - port: 50051

---
# transactions service  
apiVersion: v1
kind: Service
metadata:
  name: transactions
spec:
  type: LoadBalancer  # Creates Load Balancer #2
  ports:
    - port: 50052

---
# customer-auth service
apiVersion: v1
kind: Service
metadata:
  name: customer-auth
spec:
  type: LoadBalancer  # Creates Load Balancer #3
  ports:
    - port: 8000

# ... and so on for each service
```

**Result:**
- **6 services** = **6 Load Balancers**
- **Cost**: ~$18.25 × 6 = **~$109.50/month** ❌
- Each service gets its own external IP
- Frontend needs to know multiple endpoints
- CORS issues (different origins)

### Scenario 2: Single Load Balancer + NGINX ✅ (Current Approach)

```yaml
# Only NGINX has LoadBalancer type
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  type: LoadBalancer  # Creates Load Balancer #1 (ONLY ONE!)
  ports:
    - port: 8080

---
# All other services are ClusterIP (internal only)
apiVersion: v1
kind: Service
metadata:
  name: accounts
spec:
  type: ClusterIP  # No Load Balancer, internal only
  ports:
    - port: 50051
```

**Result:**
- **1 Load Balancer** (for NGINX only)
- **Cost**: ~$18.25/month ✅
- Single external IP
- NGINX routes internally to all services
- No CORS issues (same origin)

### Scenario 3: GCP Ingress (Alternative, but more complex)

You could use GCP Ingress Controller which creates **one Load Balancer** with path-based routing:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: martianbank-ingress
spec:
  rules:
  - http:
      paths:
      - path: /api/users
        pathType: Prefix
        backend:
          service:
            name: customer-auth
            port:
              number: 8000
      - path: /api/account
        pathType: Prefix
        backend:
          service:
            name: accounts
            port:
              number: 50051
      # ... etc for all services
```

**Result:**
- **1 Load Balancer** (created by Ingress)
- **Cost**: ~$18.25/month ✅
- But requires:
  - Reconfiguring all routing rules
  - More complex setup
  - Less flexibility than NGINX

## Cost Comparison

| Approach | Load Balancers | Monthly Cost | Complexity |
|----------|---------------|--------------|------------|
| **Each Service = LoadBalancer** | 6 | ~$109.50 | Low (but expensive) |
| **NGINX + LoadBalancer** (Current) | 1 | ~$18.25 | Medium |
| **GCP Ingress** | 1 | ~$18.25 | High |

## Visual Comparison

### Multiple Load Balancers (Bad) ❌
```
Internet
    ↓
┌─────────────────────────────────────┐
│  Load Balancer #1 (accounts)        │ → accounts:50051
│  Load Balancer #2 (transactions)    │ → transactions:50052
│  Load Balancer #3 (customer-auth)   │ → customer-auth:8000
│  Load Balancer #4 (ui)              │ → ui:3000
│  Load Balancer #5 (dashboard)       │ → dashboard:5000
│  Load Balancer #6 (atm-locator)     │ → atm-locator:8001
└─────────────────────────────────────┘
Cost: ~$109.50/month
```

### Single Load Balancer + NGINX (Good) ✅
```
Internet
    ↓
┌─────────────────────────────────────┐
│  Load Balancer #1 (NGINX only)      │ → nginx:8080
└─────────────────────────────────────┘
    ↓
NGINX Pods (internal routing)
    ↓
    ├─→ accounts (ClusterIP)
    ├─→ transactions (ClusterIP)
    ├─→ customer-auth (ClusterIP)
    ├─→ ui (ClusterIP)
    ├─→ dashboard (ClusterIP)
    └─→ atm-locator (ClusterIP)
Cost: ~$18.25/month
```

## How Kubernetes LoadBalancer Type Works

When you set `type: LoadBalancer` on a Kubernetes Service:

1. **Kubernetes** creates a Service object
2. **GCP Cloud Controller** detects the LoadBalancer type
3. **GCP automatically creates**:
   - A Forwarding Rule
   - A Target Pool or Backend Service
   - An External IP address
   - Health checks
4. **Each LoadBalancer service = One GCP Load Balancer**

So yes, **each `type: LoadBalancer` service = one GCP Load Balancer**.

## Current Configuration (Correct!)

Looking at your Helm templates:

```yaml
# Only NGINX has LoadBalancer type
{{- if .Values.nginx.enabled }}
apiVersion: v1
kind: Service
metadata:
    name: nginx
spec:
    type: LoadBalancer  # ← Only this one creates a Load Balancer
    ports:
        - port: 8080
{{- end }}

# All other services are ClusterIP (default)
apiVersion: v1
kind: Service
metadata:
    name: accounts
spec:
    # No type specified = ClusterIP (internal only)
    selector:
        app: accounts
    ports:
        - port: 50051
```

**This is correct!** Only NGINX creates a Load Balancer.

## What About Dashboard Service?

I noticed in `k8.yaml` that dashboard service also has `type: LoadBalancer`:

```yaml
apiVersion: v1
kind: Service
metadata:
    name: dashboard
spec:
    type: LoadBalancer  # ← This would create ANOTHER Load Balancer!
```

**Recommendation**: Change dashboard to `ClusterIP` since NGINX routes to it:

```yaml
apiVersion: v1
kind: Service
metadata:
    name: dashboard
spec:
    type: ClusterIP  # ← Change to ClusterIP
    selector:
        app: dashboard
    ports:
        - port: 5000
```

## Summary

### Question: "If we use only load balancer, is it created for each service?"

**Answer**: 
- **Yes**, if each service has `type: LoadBalancer`
- **No**, if only one service (NGINX) has `type: LoadBalancer` and others are `ClusterIP`

### Your Current Setup

✅ **Correct approach**: Only NGINX has `type: LoadBalancer`
- Creates **1 Load Balancer** (~$18.25/month)
- NGINX routes internally to all other services
- Other services are `ClusterIP` (internal only)

⚠️ **Check**: Make sure dashboard service is `ClusterIP`, not `LoadBalancer`

### Cost Impact

- **Current (NGINX only)**: ~$18.25/month ✅
- **If all services = LoadBalancer**: ~$109.50/month ❌
- **Savings**: ~$91.25/month by using NGINX!

## Recommendation

**Keep your current architecture:**
1. ✅ Only NGINX service = `type: LoadBalancer` (creates 1 Load Balancer)
2. ✅ All other services = `type: ClusterIP` (internal only)
3. ✅ NGINX handles routing to all services
4. ✅ Single external IP, single Load Balancer cost

This is the **most cost-effective and simplest** approach for your project!

