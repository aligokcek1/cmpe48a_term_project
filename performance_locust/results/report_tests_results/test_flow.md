
Scale limit 70 ten 60a dusur
Db indexing
Deneyler daha açık - hpa scale grafigi göster
Try slow ramp up - the system may cannot catch up - hpa threshold
Sticky session

Independent vars:
- VM cpu/memory
- HPA cpu threshold
- Node autoscaling
- DB pool size
- DB indexing
- Ramp up
- Hashing auth
- HPA min replica
- HPA max replica
- Cluster machine type

Initial configs:
VM: e2-small 2vcpu, 2gb memory
DB pool size for account and transaction: default = 100
Hashing auth = 10
HPA max min =  1
Node autoscaling is off
HPA scale CPU threshold = 70
No DB indexing


Experiment 1: Reduce ramp up
Changes on initial configs:
* Ramp up 10 to 5
Initial_200_10 vs initial 200_5


Experiment 2: Enable HPA
200_10
Changes on Initial configs:
* Customer-auth -> min 1 max 5
* Transactions -> min 1 max 2

Experiment 2.1: Enabled HPA reduced ramp up
200_5
* Same config with ex 2

Experiment 2.2: Enabled HPA, reduced target cpu utility rate
200_10
* Same config with ex 2 except cpu utility 70 to 50
  
Experiment 3: Increase VM resources
200_10
Changes on Initial configs:
* VM cpu 2 to 6
* VM memory 2 to 8

Experiment 4: Enable cluster node autoscaling
200_10
Changes on initial configs:
* Enabled cluster autoscaling

Experience 5: bcrypt 10 to 8:
200_10Changes on initial config:
* Bcrypt on auth servide reduced to 8

Experiment 5.1: Increase transaction db pool size
200_10
Differences btw ex 4:
* DB pool size increased to 200

Experiment 5.2: trans hpa max 3
200_10
Pool size resetted to initial config
Bcrypt again 8
Transaction service max replica = 3
 
Experiment 5.2.1: Reset DB to fix 500 errors
200_10
Same with 5.2 except the db is resetted.

Experiment 5.2.2: Increase auth service hpa max to 2 and reset db again
200_10
Same with 5.2.1 except auth service max pod = 2

Experiment 5.2.3: Reduce cpu util rate to 50 percent
200_10
Same with 5.2.2 but cpu util is 50 percent

Experiment 5.2.4: Set auth service min pod to 2
200_10
Same with 5.2.3 but auth service min pod = 2

Experiment 5.2.5: Enable node autoscaling
200_10
Same with 5.2.4 but node autoscaling is on

Experiment 5.2.6: test with 500_20

Experiment 5.2.7: 500_20 autoscaling OFF

Experiment 5.2.8: 500_20 HPA max 10