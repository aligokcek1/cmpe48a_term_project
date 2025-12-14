# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""
Comprehensive System Performance Test - Automated Multi-Scenario
=================================================================
This script automatically runs all 4 test scenarios sequentially:
  1. Baseline (10 users, 5 minutes)
  2. Normal Operations (50 users, 5 minutes)
  3. Peak Hours (100 users, 5 minutes)
  4. Stress Test (200 users, 5 minutes)

Components tested:
- Customer Authentication (Registration, Login, Logout)
- Account Management (Create, View, Get Details)
- Transactions (Internal Transfer, External Transfer, History)
- Loan Services (Application, History via Cloud Function)
- ATM Locator (Search via Cloud Function)

Usage:
  locust -f comprehensive_system_test.py --headless --host=http://136.119.54.74:8080

The test will automatically run all scenarios and generate reports.
"""

from locust import HttpUser, task, SequentialTaskSet, between, TaskSet, events
from locust.env import Environment
from faker import Faker
import random
import time
import logging
import os

fake = Faker()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if automated mode is enabled via environment variable
AUTOMATED_MODE = os.getenv('LOCUST_AUTOMATED_MODE', 'false').lower() == 'true'

# Test scenarios configuration
SCENARIOS = [
    {
        "name": "Scenario 1: Baseline",
        "description": "Light load - establishing performance baseline",
        "users": 10,
        "spawn_rate": 2,
        "duration": 300  # 5 minutes in seconds
    },
    {
        "name": "Scenario 2: Normal Operations",
        "description": "Moderate load - typical business hours",
        "users": 50,
        "spawn_rate": 5,
        "duration": 300  # 5 minutes
    },
    {
        "name": "Scenario 3: Peak Hours",
        "description": "High load - peak banking activity",
        "users": 100,
        "spawn_rate": 10,
        "duration": 300  # 5 minutes
    },
    {
        "name": "Scenario 4: Stress Test",
        "description": "Maximum load - system breaking point",
        "users": 200,
        "spawn_rate": 20,
        "duration": 300  # 5 minutes
    }
]

# Current scenario tracker
current_scenario = {"index": 0, "start_time": None}


class BankingUserBehavior(TaskSet):
    """
    Simulates realistic user behavior through the Martian Bank system.
    Tasks are executed randomly based on weights (not sequentially).
    """
    
    wait_time = between(3, 8)  # Realistic pause between actions

    def on_start(self):
        """
        User onboarding: Register account and create initial bank accounts
        """
        # Step 1: User Registration (Authentication Service)
        self.user_data = {
            "name": fake.name(),
            "email": f"{fake.user_name()}_{random.randint(1000, 9999)}@martian.bank",
            "password": "MartianBank123!",
            "valid": False
        }
        
        try:
            response = self.client.post(
                "/api/users/", 
                json=self.user_data,
                name="[Auth] Register User"
            )
            if response.status_code in [200, 201]:
                self.user_data["valid"] = True
                logger.info(f"✓ User registered: {self.user_data['email']}")
            else:
                logger.warning(f"✗ Registration failed: {response.status_code}")
        except Exception as e:
            logger.error(f"✗ Registration error: {str(e)}")
            self.user_data["valid"] = False
            return
        
        if not self.user_data.get("valid", False):
            return
        
        time.sleep(1)
        
        # Step 2: Login (Authentication Service)
        try:
            self.client.post(
                "/api/users/auth",
                json={
                    "email": self.user_data["email"],
                    "password": self.user_data["password"]
                },
                name="[Auth] Login"
            )
            time.sleep(1)
        except Exception:
            pass
        
        # Step 3: Create Primary Checking Account
        self.account_data = {
            "name": self.user_data["name"],
            "email_id": self.user_data["email"],
            "account_type": "Checking",
            "government_id_type": random.choice(["Driver's License", "Passport", "SSN"]),
            "govt_id_number": fake.unique.ssn(),
            "address": fake.unique.address()
        }
        
        try:
            response = self.client.post(
                "/api/accountcreate",
                data=self.account_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="[Account] Create Checking Account"
            )
            time.sleep(2)
        except Exception:
            pass
        
        # Step 4: Create Secondary Savings Account
        self.account_data["account_type"] = "Savings"
        try:
            self.client.post(
                "/api/accountcreate",
                data=self.account_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="[Account] Create Savings Account"
            )
            time.sleep(2)
        except Exception:
            pass
        
        # Step 5: Retrieve all account numbers
        try:
            response = self.client.post(
                "/api/accountallaccounts",
                data={"email_id": self.user_data["email"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="[Account] Get All Accounts"
            )
            if response.status_code == 200:
                accounts = response.json().get("response", [])
                self.account_numbers = [acc["account_number"] for acc in accounts]
            else:
                self.account_numbers = []
        except Exception:
            self.account_numbers = []

    @task(20)
    def view_account_details(self):
        """
        High frequency: Users check their account details frequently
        Weight: 20 (Most common action)
        """
        if not self.user_data.get("valid", False):
            return
        
        self.client.get(
            "/api/accountdetail",
            data={"email": self.user_data["email"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="[Account] View Account Details"
        )

    @task(15)
    def view_all_accounts(self):
        """
        High frequency: Users check all their accounts
        Weight: 15
        """
        if not self.user_data.get("valid", False):
            return
        
        self.client.post(
            "/api/accountallaccounts",
            data={"email_id": self.user_data["email"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="[Account] View All Accounts"
        )

    @task(10)
    def internal_transfer(self):
        """
        Medium frequency: Transfer between own accounts
        Weight: 10
        """
        if not self.user_data.get("valid", False) or len(self.account_numbers) < 2:
            return
        
        self.client.post(
            "/api/transaction",
            data={
                "sender_account_number": self.account_numbers[0],
                "receiver_account_number": self.account_numbers[1],
                "amount": random.randint(10, 500),
                "reason": random.choice([
                    "Savings deposit",
                    "Account rebalancing",
                    "Transfer to savings"
                ])
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="[Transaction] Internal Transfer"
        )

    @task(12)
    def check_transaction_history(self):
        """
        High frequency: Users check transaction history regularly
        Weight: 12
        """
        if not self.user_data.get("valid", False) or not self.account_numbers:
            return
        
        self.client.post(
            "/api/transactionhistory",
            data={"account_number": random.choice(self.account_numbers)},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="[Transaction] View History"
        )

    @task(5)
    def search_atm_locations(self):
        """
        Medium-low frequency: Find nearby ATMs (Cloud Function)
        Weight: 5
        """
        if not self.user_data.get("valid", False):
            return
        
        try:
            self.client.post(
                "/api/atm/",
                data={},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="[ATM] Search Locations (Cloud Function)"
            )
        except Exception:
            pass

    @task(3)
    def apply_for_loan(self):
        """
        Low frequency: Apply for a loan (Cloud Function)
        Weight: 3
        """
        if not self.user_data.get("valid", False) or not self.account_numbers:
            return
        
        loan_data = {
            "name": self.user_data["name"],
            "email": self.user_data["email"],
            "govt_id_type": self.account_data["government_id_type"],
            "govt_id_number": self.account_data["govt_id_number"],
            "account_number": self.account_numbers[0],
            "interest_rate": random.uniform(3.5, 8.5),
            "time_period": random.choice([12, 24, 36, 48, 60]),
            "loan_amount": random.randint(5000, 50000),
            "loan_type": random.choice([
                "Base Camp",
                "Rover",
                "Potato Farming",
                "Ice Home",
                "Rocker"
            ])
        }
        
        try:
            self.client.post(
                "/api/loan/",
                data=loan_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="[Loan] Submit Application (Cloud Function)"
            )
        except Exception:
            pass

    @task(4)
    def check_loan_history(self):
        """
        Low-medium frequency: Check loan application status (Cloud Function)
        Weight: 4
        """
        if not self.user_data.get("valid", False):
            return
        
        try:
            self.client.post(
                "/api/loanhistory/",
                data={"email": self.user_data["email"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="[Loan] View History (Cloud Function)"
            )
        except Exception:
            pass

    @task(2)
    def update_profile(self):
        """
        Low frequency: Update user profile
        Weight: 2
        """
        if not self.user_data.get("valid", False):
            return
        
        self.client.put(
            "/api/users/profile",
            json={
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            },
            name="[Auth] Update Profile"
        )

    @task(1)
    def logout_and_login(self):
        """
        Low frequency: Logout and login again
        Weight: 1
        """
        if not self.user_data.get("valid", False):
            return
        
        # Logout
        self.client.post(
            "/api/users/logout",
            json={"email": self.user_data["email"]},
            name="[Auth] Logout"
        )
        
        time.sleep(1)
        
        # Login again
        self.client.post(
            "/api/users/auth",
            json={
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            },
            name="[Auth] Re-login"
        )


class MartianBankUser(HttpUser):
    """
    Represents a user of the Martian Bank system.
    Configured with realistic timeouts and wait times.
    """
    host = "http://136.119.54.74:8080"
    wait_time = between(3, 8)  # Realistic pause between user sessions
    
    # Configure HTTP client timeouts
    connection_timeout = 60.0
    network_timeout = 60.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = (30.0, 60.0)  # (connect timeout, read timeout)
    
    tasks = [BankingUserBehavior]


# For running specific component tests, we can use task sets with different weights
class HeavyTransactionUser(HttpUser):
    """
    User persona: Heavy transaction user (day trader, business owner)
    Focus: Frequent transfers and balance checks
    """
    host = "http://136.119.54.74:8080"
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = (30.0, 60.0)
    
    tasks = [BankingUserBehavior]
    weight = 3  # 30% of users


class CasualBankingUser(HttpUser):
    """
    User persona: Casual banking user
    Focus: Occasional account checks and transfers
    """
    host = "http://136.119.54.74:8080"
    wait_time = between(5, 15)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = (30.0, 60.0)
    
    tasks = [BankingUserBehavior]
    weight = 7  # 70% of users


# Event handlers for automated multi-scenario testing
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Triggered when the test starts. Initializes automated scenario execution if enabled.
    """
    if not AUTOMATED_MODE:
        logger.info("=" * 80)
        logger.info("MARTIAN BANK PERFORMANCE TEST - SINGLE RUN MODE")
        logger.info("=" * 80)
        return
    
    logger.info("=" * 80)
    logger.info("MARTIAN BANK COMPREHENSIVE PERFORMANCE TEST - AUTOMATED MODE")
    logger.info("=" * 80)
    logger.info(f"Total scenarios to run: {len(SCENARIOS)}")
    logger.info("")
    
    # Start first scenario
    start_scenario(environment, 0)


def start_scenario(environment, scenario_index):
    """
    Start a specific test scenario
    """
    if scenario_index >= len(SCENARIOS):
        logger.info("=" * 80)
        logger.info("ALL SCENARIOS COMPLETED!")
        logger.info("=" * 80)
        logger.info("Check the results directory for detailed reports.")
        logger.info("Review GCP Console for infrastructure metrics.")
        environment.runner.quit()
        return
    
    scenario = SCENARIOS[scenario_index]
    current_scenario["index"] = scenario_index
    current_scenario["start_time"] = time.time()
    
    logger.info("-" * 80)
    logger.info(f"STARTING: {scenario['name']}")
    logger.info(f"Description: {scenario['description']}")
    logger.info(f"Users: {scenario['users']}")
    logger.info(f"Spawn Rate: {scenario['spawn_rate']} users/sec")
    logger.info(f"Duration: {scenario['duration']} seconds ({scenario['duration']//60} minutes)")
    logger.info("-" * 80)
    
    # Reset registration tracker for new scenario
    # No longer needed - removed deadlock-causing synchronization
    
    # Start spawning users
    if hasattr(environment.runner, 'start'):
        environment.runner.start(scenario["users"], spawn_rate=scenario["spawn_rate"])
    
    # Schedule scenario end
    environment.runner.greenlet.spawn(monitor_scenario, environment, scenario_index)


def monitor_scenario(environment, scenario_index):
    """
    Monitor scenario duration and transition to next scenario
    """
    scenario = SCENARIOS[scenario_index]
    
    # Wait for scenario duration
    time.sleep(scenario["duration"])
    
    logger.info("-" * 80)
    logger.info(f"COMPLETED: {scenario['name']}")
    logger.info(f"Duration: {scenario['duration']} seconds")
    logger.info("-" * 80)
    
    # Stop current users
    if hasattr(environment.runner, 'stop'):
        environment.runner.stop()
    
    # Wait a bit before starting next scenario (cooldown period)
    cooldown = 30
    logger.info(f"Cooldown period: {cooldown} seconds before next scenario...")
    time.sleep(cooldown)
    
    # Start next scenario
    start_scenario(environment, scenario_index + 1)


@events.spawning_complete.add_listener
def on_spawning_complete(user_count, **kwargs):
    """
    Called when all users have been spawned for current scenario
    """
    scenario = SCENARIOS[current_scenario["index"]]
    logger.info(f"✓ All {user_count} users spawned for {scenario['name']}")
    logger.info(f"✓ Test in progress... ({scenario['duration']//60} minutes remaining)")


@events.quitting.add_listener  
def on_quitting(environment, **kwargs):
    """
    Called when Locust is shutting down
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUITE COMPLETE - Shutting down")
    logger.info("=" * 80)
